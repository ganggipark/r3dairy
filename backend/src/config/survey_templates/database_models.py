"""Database models for survey configurations and responses.

Note: This project uses Supabase (PostgreSQL) for database.
These are Pydantic models for API validation, not SQLAlchemy ORM models.
Actual database schema is defined in backend/src/db/schema.sql
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class SurveyStatus(str, Enum):
    """Survey configuration status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class SurveySource(str, Enum):
    """Survey response source platform."""
    N8N = "n8n"
    GOOGLE_FORMS = "google_forms"
    WEB = "web"
    API = "api"


class SurveyConfiguration(BaseModel):
    """Survey configuration stored in database."""
    id: str = Field(..., description="Unique survey ID (matches FormConfiguration.id)")
    name: str = Field(..., description="Survey name")
    description: str = Field(default="", description="Survey description")
    form_json: Dict[str, Any] = Field(..., description="Full FormConfiguration as JSON")
    status: SurveyStatus = Field(default=SurveyStatus.DRAFT, description="Survey status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_to: Dict[str, bool] = Field(
        default_factory=lambda: {"n8n": False, "google_forms": False, "web": False},
        description="Deployment status for each platform"
    )
    response_count: int = Field(default=0, description="Number of responses received")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "survey_abc123",
                "name": "R³ Diary - Personal Assessment Survey",
                "description": "Help us create your personalized diary experience",
                "form_json": {"name": "...", "sections": []},
                "status": "active",
                "deployed_to": {"n8n": True, "web": True, "google_forms": False},
                "response_count": 42,
                "metadata": {"template": "default", "locale": "en-US"}
            }
        }


class SurveyResponse(BaseModel):
    """Individual survey response."""
    id: str = Field(..., description="Unique response ID")
    survey_id: str = Field(..., description="Survey configuration ID")
    response_data: Dict[str, Any] = Field(..., description="Raw field answers as submitted")
    normalized_data: Dict[str, Any] = Field(..., description="Standardized/normalized format")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(None, description="Submitter IP address")
    source: SurveySource = Field(default=SurveySource.WEB, description="Submission source")
    user_id: Optional[str] = Field(None, description="Linked user ID (if authenticated)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "response_xyz789",
                "survey_id": "survey_abc123",
                "response_data": {
                    "name": "김학생",
                    "email": "student@example.com",
                    "birth_date": "2005-03-15",
                    "primary_role": "Student"
                },
                "normalized_data": {
                    "name": "김학생",
                    "email": "student@example.com",
                    "birth_date": "2005-03-15",
                    "role": "student",
                    "personality_scores": {
                        "p_extroversion": 4,
                        "p_structured": 3
                    }
                },
                "submitted_at": "2026-01-29T10:30:00Z",
                "ip_address": "192.168.1.1",
                "source": "web"
            }
        }


class SurveyResponseCreate(BaseModel):
    """Request model for creating a survey response."""
    survey_id: str
    response_data: Dict[str, Any]
    source: SurveySource = SurveySource.WEB
    user_id: Optional[str] = None


class SurveyResponseSummary(BaseModel):
    """Summary statistics for survey responses."""
    survey_id: str
    total_responses: int
    responses_by_source: Dict[str, int]
    responses_by_date: Dict[str, int]
    completion_rate: float = Field(description="Percentage of completed vs. abandoned surveys")
    average_completion_time_seconds: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "survey_id": "survey_abc123",
                "total_responses": 150,
                "responses_by_source": {"web": 100, "n8n": 50},
                "responses_by_date": {"2026-01-29": 25, "2026-01-28": 30},
                "completion_rate": 0.87,
                "average_completion_time_seconds": 245.5
            }
        }


class SurveyDeployment(BaseModel):
    """Deployment record for a survey."""
    survey_id: str
    target: str = Field(description="Deployment target: n8n, google_forms, web")
    deployed_at: datetime = Field(default_factory=datetime.utcnow)
    deployment_config: Dict[str, Any] = Field(description="Platform-specific configuration")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for submissions")
    status: str = Field(default="active", description="Deployment status")

    class Config:
        json_schema_extra = {
            "example": {
                "survey_id": "survey_abc123",
                "target": "n8n",
                "deployed_at": "2026-01-29T10:00:00Z",
                "deployment_config": {"workflow_id": "workflow_123"},
                "webhook_url": "https://n8n.example.com/webhook/survey_abc123",
                "status": "active"
            }
        }


# SQL Schema for Supabase
SUPABASE_SCHEMA = """
-- Survey Configurations Table
CREATE TABLE IF NOT EXISTS survey_configurations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    form_json JSONB NOT NULL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deployed_to JSONB DEFAULT '{"n8n": false, "google_forms": false, "web": false}'::jsonb,
    response_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Survey Responses Table
CREATE TABLE IF NOT EXISTS survey_responses (
    id TEXT PRIMARY KEY,
    survey_id TEXT NOT NULL REFERENCES survey_configurations(id) ON DELETE CASCADE,
    response_data JSONB NOT NULL,
    normalized_data JSONB NOT NULL,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address TEXT,
    source TEXT DEFAULT 'web' CHECK (source IN ('n8n', 'google_forms', 'web', 'api')),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Survey Deployments Table
CREATE TABLE IF NOT EXISTS survey_deployments (
    id SERIAL PRIMARY KEY,
    survey_id TEXT NOT NULL REFERENCES survey_configurations(id) ON DELETE CASCADE,
    target TEXT NOT NULL CHECK (target IN ('n8n', 'google_forms', 'web')),
    deployed_at TIMESTAMPTZ DEFAULT NOW(),
    deployment_config JSONB NOT NULL,
    webhook_url TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey_id ON survey_responses(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_submitted_at ON survey_responses(submitted_at);
CREATE INDEX IF NOT EXISTS idx_survey_responses_source ON survey_responses(source);
CREATE INDEX IF NOT EXISTS idx_survey_responses_user_id ON survey_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_survey_deployments_survey_id ON survey_deployments(survey_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_survey_configurations_updated_at
    BEFORE UPDATE ON survey_configurations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Response count trigger
CREATE OR REPLACE FUNCTION increment_response_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE survey_configurations
    SET response_count = response_count + 1
    WHERE id = NEW.survey_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_survey_response_count
    AFTER INSERT ON survey_responses
    FOR EACH ROW
    EXECUTE FUNCTION increment_response_count();

-- RLS Policies (Row Level Security)
ALTER TABLE survey_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_deployments ENABLE ROW LEVEL SECURITY;

-- Allow public read of active surveys
CREATE POLICY "Public can view active surveys"
    ON survey_configurations FOR SELECT
    USING (status = 'active');

-- Allow authenticated users to submit responses
CREATE POLICY "Authenticated users can submit responses"
    ON survey_responses FOR INSERT
    WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'anon');

-- Allow users to view their own responses
CREATE POLICY "Users can view own responses"
    ON survey_responses FOR SELECT
    USING (user_id = auth.uid() OR auth.role() = 'service_role');

-- Admin policies (requires service role)
CREATE POLICY "Service role full access to configurations"
    ON survey_configurations FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to responses"
    ON survey_responses FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to deployments"
    ON survey_deployments FOR ALL
    USING (auth.role() = 'service_role');
"""
