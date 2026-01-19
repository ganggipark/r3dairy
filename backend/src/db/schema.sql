-- R³ Diary System Database Schema
-- Supabase PostgreSQL Database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PROFILES TABLE
-- ============================================================================
-- User profile with birth information and preferences
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    birth_place VARCHAR(200) NOT NULL,
    birth_place_lat DECIMAL(10, 8),
    birth_place_lng DECIMAL(11, 8),
    roles JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example: ["student", "freelancer"]
    preferences JSONB DEFAULT '{}'::jsonb,
    -- Example: {"interests": ["work", "health"], "rhythm_type": "morning", "record_style": "detailed"}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DAILY RHYTHM SIGNALS TABLE
-- ============================================================================
-- Internal calculation results (NEVER exposed to users)
-- Contains technical terms like 사주명리, 기문둔갑 calculations
CREATE TABLE daily_rhythm_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    rhythm_data JSONB NOT NULL,
    -- Internal representation with technical terms
    -- Example: {"천간": "甲", "지지": "子", "오행": {...}, "십성": {...}}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(profile_id, date)
);

-- Index for fast date lookup
CREATE INDEX idx_daily_rhythm_signals_date ON daily_rhythm_signals(profile_id, date);

-- ============================================================================
-- DAILY CONTENT TABLE
-- ============================================================================
-- User-facing content (translated from rhythm signals)
-- Follows DAILY_CONTENT_SCHEMA.json structure
CREATE TABLE daily_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    role VARCHAR(50) NOT NULL,
    -- Which role this translation is for
    content_json JSONB NOT NULL,
    -- Follows DAILY_CONTENT_SCHEMA.json
    -- Example: {"summary": "...", "keywords": [...], "rhythm_description": "..."}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(profile_id, date, role)
);

-- Index for fast date and role lookup
CREATE INDEX idx_daily_content_date_role ON daily_content(profile_id, date, role);

-- ============================================================================
-- DAILY LOGS TABLE
-- ============================================================================
-- User's daily records (right panel in UI)
CREATE TABLE daily_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    schedule TEXT,
    -- Daily schedule/plan
    todos JSONB DEFAULT '[]'::jsonb,
    -- Todo items: [{"text": "...", "done": false}]
    mood INTEGER CHECK (mood >= 1 AND mood <= 5),
    -- 1-5 scale
    energy INTEGER CHECK (energy >= 1 AND energy <= 5),
    -- 1-5 scale
    notes TEXT,
    -- Free-form notes
    gratitude TEXT,
    -- Gratitude journaling
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(profile_id, date)
);

-- Index for fast date lookup
CREATE INDEX idx_daily_logs_date ON daily_logs(profile_id, date);

-- ============================================================================
-- ROLE TEMPLATES TABLE
-- ============================================================================
-- Translation templates for each role
CREATE TABLE role_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    -- "student", "office_worker", "freelancer", etc.
    template_data JSONB NOT NULL,
    -- Translation rules and templates
    -- Example: {"action_guide": {"do": [...], "avoid": [...]}, "examples": [...]}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- MONTHLY CONTENT TABLE
-- ============================================================================
-- Monthly content (theme, priorities, calendar)
CREATE TABLE monthly_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
    role VARCHAR(50) NOT NULL,
    theme TEXT NOT NULL,
    -- Monthly theme
    priorities JSONB DEFAULT '[]'::jsonb,
    -- Top 3 priorities: ["priority1", "priority2", "priority3"]
    calendar_data JSONB DEFAULT '{}'::jsonb,
    -- Date-wise keywords: {"1": "keyword", "2": "keyword", ...}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(profile_id, year, month, role)
);

-- Index for fast year/month lookup
CREATE INDEX idx_monthly_content_year_month ON monthly_content(profile_id, year, month);

-- ============================================================================
-- YEARLY CONTENT TABLE
-- ============================================================================
-- Yearly content (flow summary, monthly signals)
CREATE TABLE yearly_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    summary TEXT NOT NULL,
    -- Yearly flow summary
    keywords JSONB DEFAULT '[]'::jsonb,
    -- Key themes for the year
    monthly_signals JSONB DEFAULT '{}'::jsonb,
    -- Monthly flow indicators: {"1": {...}, "2": {...}, ...}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(profile_id, year, role)
);

-- Index for fast year lookup
CREATE INDEX idx_yearly_content_year ON yearly_content(profile_id, year);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_rhythm_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE yearly_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_templates ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can view and update their own profile
CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Daily Rhythm Signals: Backend only (users cannot access directly)
CREATE POLICY "Users cannot access rhythm signals"
    ON daily_rhythm_signals FOR ALL
    USING (false);

-- Daily Content: Users can view their own content
CREATE POLICY "Users can view own daily content"
    ON daily_content FOR SELECT
    USING (auth.uid() = profile_id);

-- Daily Logs: Users can manage their own logs
CREATE POLICY "Users can manage own logs"
    ON daily_logs FOR ALL
    USING (auth.uid() = profile_id);

-- Monthly Content: Users can view their own content
CREATE POLICY "Users can view own monthly content"
    ON monthly_content FOR SELECT
    USING (auth.uid() = profile_id);

-- Yearly Content: Users can view their own content
CREATE POLICY "Users can view own yearly content"
    ON yearly_content FOR SELECT
    USING (auth.uid() = profile_id);

-- Role Templates: Public read access
CREATE POLICY "Anyone can read role templates"
    ON role_templates FOR SELECT
    USING (true);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_logs_updated_at
    BEFORE UPDATE ON daily_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_role_templates_updated_at
    BEFORE UPDATE ON role_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert default role templates
INSERT INTO role_templates (role_name, template_data) VALUES
('student', '{
    "focus_areas": ["학습", "집중", "페이스 관리"],
    "avoid_terms": ["계약", "리더십", "보고"],
    "examples": ["과제 집중", "시험 준비", "공부 계획"]
}'::jsonb),
('office_worker', '{
    "focus_areas": ["업무", "관계", "결정", "보고"],
    "avoid_terms": ["시험", "과제"],
    "examples": ["회의 준비", "업무 조율", "보고서 작성"]
}'::jsonb),
('freelancer', '{
    "focus_areas": ["결정", "계약", "창작", "체력"],
    "avoid_terms": ["출근", "회의"],
    "examples": ["프로젝트 진행", "클라이언트 미팅", "작업 일정"]
}'::jsonb)
ON CONFLICT (role_name) DO NOTHING;
