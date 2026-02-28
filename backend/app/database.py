import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


# DB 파일을 backend 폴더 기준으로 고정 (실행 경로에 상관없이 동일한 DB 사용)
_db_dir = Path(__file__).resolve().parent.parent
_db_path = _db_dir / "jscorp_hr.db"
DATABASE_URL = f"sqlite:///{_db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_users_columns(engine)
    _migrate_employees_user_column(engine)
    _migrate_leave_request_columns(engine)
    _migrate_evaluation_result_columns(engine)


def _migrate_users_columns(eng):
    from sqlalchemy import text
    with eng.connect() as conn:
        for col, typ in [
            ("email", "VARCHAR(255)"),
            ("email_verified", "INTEGER DEFAULT 0"),
            ("role", "VARCHAR(50) DEFAULT 'EMPLOYEE'"),
            ("reset_token", "VARCHAR(255)"),
            ("reset_token_expires", "DATETIME"),
            ("verification_token", "VARCHAR(255)"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {typ}"))
                conn.commit()
            except Exception:
                conn.rollback()


def _migrate_employees_user_column(eng):
    from sqlalchemy import text

    with eng.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE employees ADD COLUMN user_id INTEGER"))
            conn.commit()
        except Exception:
            conn.rollback()


def _migrate_leave_request_columns(eng):
    from sqlalchemy import text

    with eng.connect() as conn:
        for col, typ in [
            ("approver_emp_id", "INTEGER"),
            ("approved_at", "DATETIME"),
        ]:
            try:
                conn.execute(
                    text(f"ALTER TABLE leave_requests ADD COLUMN {col} {typ}")
                )
                conn.commit()
            except Exception:
                conn.rollback()


def _migrate_evaluation_result_columns(eng):
    from sqlalchemy import text

    with eng.connect() as conn:
        for col, typ in [
            ("evaluator_emp_id", "INTEGER"),
            ("grade", "VARCHAR(10)"),
            ("is_promotion_candidate", "INTEGER DEFAULT 0"),
        ]:
            try:
                conn.execute(
                    text(f"ALTER TABLE evaluation_results ADD COLUMN {col} {typ}")
                )
                conn.commit()
            except Exception:
                conn.rollback()

