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
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="EMPLOYEE")
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_token: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
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
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    department: Mapped["Department"] = relationship(backref="employees")
    user: Mapped["User"] = relationship()


class EmployeeJobHistory(Base):
    __tablename__ = "employee_job_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    from_dept_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_dept_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    change_date: Mapped[date] = mapped_column(Date, default=date.today)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship()


class EmployeeStatusHistory(Base):
    __tablename__ = "employee_status_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20))
    change_date: Mapped[date] = mapped_column(Date, default=date.today)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    employee: Mapped["Employee"] = relationship()


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
    approver_emp_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("employees.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship(foreign_keys=[emp_id])
    approver: Mapped["Employee"] = relationship(foreign_keys=[approver_emp_id])


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


class PermissionRequest(Base):
    __tablename__ = "permission_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    target_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    requested_role: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )


class EvaluationPlan(Base):
    __tablename__ = "evaluation_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN / CLOSED
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class EvaluationItem(Base):
    __tablename__ = "evaluation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_plans.id"))
    name: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    category: Mapped[str | None] = mapped_column(String(20), nullable=True)  # SELF/MANAGER/PEER

    plan: Mapped["EvaluationPlan"] = relationship()


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_plans.id"))
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    evaluator_emp_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("employees.id"), nullable=True
    )  # None = self, else manager/peer
    score: Mapped[float] = mapped_column(DECIMAL(5, 2))
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_promotion_candidate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    plan: Mapped["EvaluationPlan"] = relationship()
    employee: Mapped["Employee"] = relationship(foreign_keys=[emp_id])
    evaluator: Mapped["Employee"] = relationship(foreign_keys=[evaluator_emp_id])


class EvaluationScore(Base):
    __tablename__ = "evaluation_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    result_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_results.id"))
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_items.id"))
    score: Mapped[float] = mapped_column(DECIMAL(5, 2))
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    result: Mapped["EvaluationResult"] = relationship()
    item: Mapped["EvaluationItem"] = relationship()


class EvaluationTarget(Base):
    __tablename__ = "evaluation_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_plans.id"))
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")

    plan: Mapped["EvaluationPlan"] = relationship()
    employee: Mapped["Employee"] = relationship()


class EvaluationEvaluator(Base):
    __tablename__ = "evaluation_evaluators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_targets.id"))
    evaluator_emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    relation: Mapped[str] = mapped_column(String(20))  # SELF/MANAGER/PEER
    status: Mapped[str] = mapped_column(String(20), default="PENDING")

    target: Mapped["EvaluationTarget"] = relationship()
    evaluator: Mapped["Employee"] = relationship()


class GradePolicy(Base):
    __tablename__ = "grade_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("evaluation_plans.id"))
    min_score: Mapped[float] = mapped_column(DECIMAL(5, 2))
    max_score: Mapped[float] = mapped_column(DECIMAL(5, 2))
    grade: Mapped[str] = mapped_column(String(10))
    is_promotion_candidate: Mapped[bool] = mapped_column(Boolean, default=False)

    plan: Mapped["EvaluationPlan"] = relationship()


class TrainingCourse(Base):
    __tablename__ = "training_courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_courses.id"))
    title: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    course: Mapped["TrainingCourse"] = relationship()


class TrainingEnrollment(Base):
    __tablename__ = "training_enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_sessions.id"))
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    status: Mapped[str] = mapped_column(
        String(20), default="REQUESTED"
    )  # REQUESTED / APPROVED / COMPLETED / CANCELLED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    session: Mapped["TrainingSession"] = relationship()
    employee: Mapped["Employee"] = relationship()


class BenefitPolicy(Base):
    __tablename__ = "benefit_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    policy_type: Mapped[str] = mapped_column(String(20))  # POINT, MEAL, HOUSING, etc.
    default_points: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class PointBalance(Base):
    __tablename__ = "point_balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    policy_id: Mapped[int] = mapped_column(Integer, ForeignKey("benefit_policies.id"))
    balance: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    year: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    employee: Mapped["Employee"] = relationship()
    policy: Mapped["BenefitPolicy"] = relationship()


class PointTransaction(Base):
    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    balance_id: Mapped[int] = mapped_column(Integer, ForeignKey("point_balances.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2))
    txn_type: Mapped[str] = mapped_column(String(20))  # GRANT, USE, EXPIRE, ADJUST
    memo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    balance: Mapped["PointBalance"] = relationship()


class CodeGroup(Base):
    __tablename__ = "code_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("code_groups.id"))
    code: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    group: Mapped["CodeGroup"] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50))
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_value: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    new_value: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()

