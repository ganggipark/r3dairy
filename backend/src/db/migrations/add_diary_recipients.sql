-- Migration: add_diary_recipients
-- diary 대상자 관리 테이블 생성

CREATE TABLE diary_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL DEFAULT '00:00:00',
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('male', 'female', 'other')),
    birth_place VARCHAR(200) NOT NULL DEFAULT '',
    role VARCHAR(50) NOT NULL DEFAULT 'office_worker',
    relationship VARCHAR(50),
    notes TEXT,
    diary_period VARCHAR(20) DEFAULT 'monthly',
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_diary_recipients_owner ON diary_recipients(owner_id);

-- UNIQUE index: owner당 is_default=true가 1개만 허용
CREATE UNIQUE INDEX idx_diary_recipients_default
    ON diary_recipients(owner_id, is_default)
    WHERE is_default = true;

ALTER TABLE diary_recipients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own recipients"
    ON diary_recipients FOR SELECT
    USING (owner_id = auth.uid());

CREATE POLICY "Users can insert own recipients"
    ON diary_recipients FOR INSERT
    WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Users can update own recipients"
    ON diary_recipients FOR UPDATE
    USING (owner_id = auth.uid());

CREATE POLICY "Users can delete own recipients"
    ON diary_recipients FOR DELETE
    USING (owner_id = auth.uid());
