# Survey Database Setup Instructions

## Step 1: Execute SQL Schema in Supabase

1. Open Supabase Dashboard
2. Navigate to: **SQL Editor**
3. Copy and paste the following SQL (from `backend/src/config/survey_templates/database_models.py` lines 156-264):

```sql
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
```

4. Click **Run** to execute the SQL

## Step 2: Verify Tables Created

Run this query to verify tables exist:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('survey_configurations', 'survey_responses', 'survey_deployments');
```

Expected output: 3 rows

## Migration Complete

After executing the SQL:
- ✅ Survey configurations will persist across server restarts
- ✅ Survey responses will be stored in Supabase
- ✅ Response counts auto-increment via database triggers
- ✅ RLS policies protect data access

## API Endpoints Now Using Supabase

All these endpoints now use persistent storage:

- `POST /surveys/create` → Saves to `survey_configurations`
- `GET /surveys/{id}` → Reads from `survey_configurations`
- `POST /surveys/submit` → Saves to `survey_responses` (triggers count increment)
- `GET /surveys/{id}/responses` → Reads from `survey_responses`
- `PUT /surveys/{id}/status` → Updates `survey_configurations`
