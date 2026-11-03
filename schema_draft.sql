-- =====================================================================
-- CẤU TRÚC DATABASE - KHỚP VỚI main.py (FastAPI) CỦA BẠN
-- Chạy trong Supabase: SQL Editor > New query > dán toàn bộ > Run
-- An toàn khi chạy lại nhiều lần: không xóa, không ghi đè dữ liệu.
-- =====================================================================

CREATE TABLE IF NOT EXISTS teachers (
    id             SERIAL PRIMARY KEY,
    teacher_code   VARCHAR(30)  NOT NULL UNIQUE,
    full_name      VARCHAR(150) NOT NULL,
    phone          VARCHAR(20),
    license_number VARCHAR(50),
    status         VARCHAR(30)  NOT NULL DEFAULT 'active',
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicles (
    id             SERIAL PRIMARY KEY,
    plate_number   VARCHAR(20)  NOT NULL UNIQUE,
    brand          VARCHAR(80),
    model          VARCHAR(80),
    license_class  VARCHAR(10),
    year           INTEGER,
    status         VARCHAR(30)  NOT NULL DEFAULT 'active',
    created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS students (
    id              SERIAL PRIMARY KEY,
    student_code    VARCHAR(30)  NOT NULL UNIQUE,
    full_name       VARCHAR(150) NOT NULL,
    phone           VARCHAR(20),
    date_of_birth   DATE,
    address         VARCHAR(255),
    license_class   VARCHAR(10)  NOT NULL,
    tuition_fee     NUMERIC(14,0) NOT NULL DEFAULT 0,
    status          VARCHAR(30)  NOT NULL DEFAULT 'Đang học',
    teacher_id      INTEGER REFERENCES teachers(id) ON DELETE SET NULL,
    enrollment_date DATE         NOT NULL DEFAULT CURRENT_DATE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lessons (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    teacher_id   INTEGER NOT NULL REFERENCES teachers(id) ON DELETE RESTRICT,
    vehicle_id   INTEGER REFERENCES vehicles(id) ON DELETE SET NULL,
    lesson_date  DATE,
    start_time   VARCHAR(10),
    end_time     VARCHAR(10),
    duration     NUMERIC(4,1) NOT NULL DEFAULT 0,
    lesson_type  VARCHAR(100),
    content      TEXT,
    notes        TEXT,
