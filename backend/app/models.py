from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    effective_from: Mapped[date] = mapped_column(Date, default=date.today)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    headcount_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    parent: Mapped["Department"] = relationship(remote_side=[id])


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emp_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hire_date: Mapped[date] = mapped_column(Date, default=date.today)
    terminate_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    dept_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    pay_group_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("pay_groups.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    department: Mapped["Department"] = relationship(backref="employees")


class WorkCalendar(Base):
    __tablename__ = "work_calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    is_workday: Mapped[bool] = mapped_column(Boolean, default=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False)
    holiday_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WorkType(Base):
    __tablename__ = "work_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str] = mapped_column(String(5))
    break_minutes: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    work_date: Mapped[date] = mapped_column(Date)
    work_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_types.id"))
    planned_start: Mapped[datetime] = mapped_column(DateTime)
    planned_end: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship()
    work_type: Mapped["WorkType"] = relationship()


class TimeLog(Base):
    __tablename__ = "time_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    log_datetime: Mapped[datetime] = mapped_column(DateTime)
    log_type: Mapped[str] = mapped_column(String(10))  # IN / OUT
    source: Mapped[str] = mapped_column(String(20), default="DEVICE")
    device_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship()


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    leave_type: Mapped[str] = mapped_column(String(20))
    start_datetime: Mapped[datetime] = mapped_column(DateTime)
    end_datetime: Mapped[datetime] = mapped_column(DateTime)
    hours: Mapped[float] = mapped_column(DECIMAL(5, 2))
    status: Mapped[str] = mapped_column(String(20), default="REQUESTED")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship()


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    year: Mapped[int] = mapped_column(Integer)
    entitled_days: Mapped[float] = mapped_column(DECIMAL(5, 2))
    used_days: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    remaining_days: Mapped[float] = mapped_column(DECIMAL(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship()


class AttendanceMonthSummary(Base):
    __tablename__ = "attendance_month_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    year_month: Mapped[str] = mapped_column(String(6), index=True)
    planned_hours: Mapped[float] = mapped_column(DECIMAL(7, 2), default=0)
    worked_hours: Mapped[float] = mapped_column(DECIMAL(7, 2), default=0)
    overtime_hours: Mapped[float] = mapped_column(DECIMAL(7, 2), default=0)
    night_hours: Mapped[float] = mapped_column(DECIMAL(7, 2), default=0)
    holiday_hours: Mapped[float] = mapped_column(DECIMAL(7, 2), default=0)
    late_count: Mapped[int] = mapped_column(Integer, default=0)
    early_leave_count: Mapped[int] = mapped_column(Integer, default=0)
    absence_count: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship()


class PayGroup(Base):
    __tablename__ = "pay_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    pay_cycle: Mapped[str] = mapped_column(String(20), default="MONTHLY")
    cutoff_day: Mapped[int] = mapped_column(Integer, default=25)
    pay_day: Mapped[int] = mapped_column(Integer, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PayItem(Base):
    __tablename__ = "pay_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    item_type: Mapped[str] = mapped_column(String(20))  # EARNING / DEDUCTION
    taxable: Mapped[bool] = mapped_column(Boolean, default=True)
    calculation_type: Mapped[str] = mapped_column(
        String(20), default="FIXED"
    )  # FIXED / RATE / FORMULA
    default_amount: Mapped[float | None] = mapped_column(DECIMAL(15, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PayRun(Base):
    __tablename__ = "pay_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pay_group_id: Mapped[int] = mapped_column(Integer, ForeignKey("pay_groups.id"))
    year_month: Mapped[str] = mapped_column(String(6), index=True)
    run_type: Mapped[str] = mapped_column(String(20), default="REGULAR")
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    pay_group: Mapped["PayGroup"] = relationship()


class PayResult(Base):
    __tablename__ = "pay_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pay_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("pay_runs.id"))
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    gross_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), default=0)
    deduct_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), default=0)
    net_amount: Mapped[float] = mapped_column(DECIMAL(15, 2), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="KRW")
    status: Mapped[str] = mapped_column(String(20), default="CALCULATED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    pay_run: Mapped["PayRun"] = relationship()
    employee: Mapped["Employee"] = relationship()


class PayResultItem(Base):
    __tablename__ = "pay_result_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pay_result_id: Mapped[int] = mapped_column(Integer, ForeignKey("pay_results.id"))
    pay_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("pay_items.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(15, 2))
    quantity: Mapped[float] = mapped_column(DECIMAL(10, 2), default=1)
    rate: Mapped[float | None] = mapped_column(DECIMAL(10, 4), nullable=True)
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    pay_result: Mapped["PayResult"] = relationship()
    pay_item: Mapped["PayItem"] = relationship()

