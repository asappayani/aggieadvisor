-- ============================================================
--  professors  •  one row per instructor  (RateMyProfessor data lives here)
-- ============================================================
CREATE TABLE IF NOT EXISTS professors (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,      -- SERIAL in Postgres
    name           TEXT UNIQUE NOT NULL,                   -- 'Bhargava D'
    rmp_avg        REAL,        -- overall rating (1–5, nullable)
    rmp_difficulty REAL,        -- difficulty (1–5)
    rmp_count      INTEGER,     -- number of ratings
    rmp_url        TEXT,        -- canonical RMP profile URL
    rmp_updated    DATETIME     -- last scrape timestamp (UTC)
);

-- Quick LIKE/ILIKE search if you build a UI picker
CREATE INDEX IF NOT EXISTS idx_prof_name_like
  ON professors (name COLLATE NOCASE);

----------------------------------------------------------------
--  Optional helper view – newest RMP snapshot per prof
----------------------------------------------------------------
CREATE VIEW IF NOT EXISTS professor_ratings AS
SELECT
    id,
    name,
    rmp_avg,
    rmp_difficulty,
    rmp_count
FROM professors;
-- (You can refine this view later if you add rating history)

-- ============================================================
--  courses  •  one row per course-section per term
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,    -- SERIAL in Postgres

    -- identity
    course        TEXT NOT NULL,          -- 'AERO-201'
    professor     TEXT NOT NULL,          -- human-readable copy
    professor_id  INTEGER,                -- FK (nullable during migration)

    -- term metadata
    semester      TEXT NOT NULL CHECK (semester IN ('FALL','SPRING','SUMMER')),
    year          INTEGER NOT NULL,

    -- org metadata
    college       TEXT NOT NULL,
    department    TEXT NOT NULL,

    -- grade counts
    a_count       INTEGER NOT NULL,
    b_count       INTEGER NOT NULL,
    c_count       INTEGER NOT NULL,
    d_count       INTEGER NOT NULL,
    f_count       INTEGER NOT NULL,
    total_count   INTEGER NOT NULL,
    gpa           REAL    NOT NULL,

    -- misc flags
    q_drop        INTEGER NOT NULL,

    -- audit
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- referential integrity (enforced in Postgres; informational in SQLite)
    FOREIGN KEY (professor_id) REFERENCES professors(id)
);

----------------------------------------------------------------
--  Uniqueness & performance indexes
----------------------------------------------------------------
-- Prevent duplicate loads of the same course/term/instructor
CREATE UNIQUE INDEX IF NOT EXISTS uniq_course_term_instr
  ON courses (course, semester, year, professor);

-- Common query filters
CREATE INDEX IF NOT EXISTS idx_department       ON courses (department);
CREATE INDEX IF NOT EXISTS idx_semester_year    ON courses (semester, year);

----------------------------------------------------------------
--  Trigger to update updated_at (no-op in SQLite < 3.37; ready for Postgres)
----------------------------------------------------------------
-- Uncomment in Postgres:
-- CREATE OR REPLACE FUNCTION trg_set_updated_at()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     NEW.updated_at = CURRENT_TIMESTAMP;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- CREATE TRIGGER trg_courses_timestamp
-- BEFORE UPDATE ON courses
-- FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();
