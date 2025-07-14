-- Courses table schema
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Will be SERIAL in PostgreSQL
    course TEXT NOT NULL,                  -- e.g., 'AERO-201'
    a_count INTEGER NOT NULL,              -- Number of A grades
    b_count INTEGER NOT NULL,              -- Number of B grades
    c_count INTEGER NOT NULL,              -- Number of C grades
    d_count INTEGER NOT NULL,              -- Number of D grades
    f_count INTEGER NOT NULL,              -- Number of F grades
    total_count INTEGER NOT NULL,          -- Total number of students
    gpa DECIMAL(4,3) NOT NULL,             -- e.g., 3.500
    q_drop INTEGER NOT NULL,               -- Q-drop count (0 or 1)
    professor TEXT NOT NULL,               -- e.g., 'BHARGAVA D'
    semester TEXT NOT NULL,                -- e.g., 'FALL'
    year INTEGER NOT NULL,                 -- e.g., 2024
    college TEXT NOT NULL,                 -- e.g., 'ENGINEERING'
    department TEXT NOT NULL,              -- e.g., 'AEROSPACE ENGINEERING'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX idx_course_professor ON courses(course, professor);
CREATE INDEX idx_department ON courses(department);
CREATE INDEX idx_semester_year ON courses(semester, year);

-- Note: When migrating to PostgreSQL (Supabase), make these changes:
-- 1. Change INTEGER PRIMARY KEY AUTOINCREMENT to SERIAL PRIMARY KEY
-- 2. Change TIMESTAMP to TIMESTAMPTZ
-- 3. Add proper triggers for updated_at:
/*
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
*/
