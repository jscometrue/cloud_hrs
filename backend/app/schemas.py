from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None
    email_verified: bool = False
    role: str = "EMPLOYEE"


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    email: str | None = None
    email_verified: bool = False
    role: str = "EMPLOYEE"

    class Config:
        from_attributes = True


class ResetPasswordRequest(BaseModel):
    new_password: str


class RequestVerificationRequest(BaseModel):
    username: str


class RequestPasswordResetRequest(BaseModel):
    username: str


class ResetPasswordByTokenRequest(BaseModel):
    token: str
    new_password: str


class DepartmentBase(BaseModel):
    code: str
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    code: str | None = None
    name: str | None = None


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    emp_no: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    hire_date: date
    status: str = "ACTIVE"
    dept_id: int | None = None
    pay_group_id: int | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    emp_no: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    hire_date: date | None = None
    status: str | None = None
    dept_id: int | None = None
    pay_group_id: int | None = None


class EmployeeRead(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


class WorkTypeBase(BaseModel):
    code: str
    name: str
    start_time: str = "09:00"
    end_time: str = "18:00"
    break_minutes: int = 60


class WorkTypeCreate(WorkTypeBase):
    pass


class WorkTypeUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    break_minutes: int | None = None


class WorkTypeRead(WorkTypeBase):
    id: int

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    emp_id: int
    leave_type: str
    start_datetime: datetime
    end_datetime: datetime
    hours: Decimal
    reason: str | None = None


class LeaveRequestRead(BaseModel):
    id: int
    emp_id: int
    leave_type: str
    start_datetime: datetime
    end_datetime: datetime
    hours: Decimal
    status: str
    reason: str | None = None
    approver_emp_id: int | None = None
    approved_at: datetime | None = None

    class Config:
        from_attributes = True


class PayItemBase(BaseModel):
    code: str
    name: str
    item_type: str = "EARNING"
    taxable: bool = True
    calculation_type: str = "FIXED"
    default_amount: Decimal | None = None


class PayItemCreate(PayItemBase):
    pass


class PayItemUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    item_type: str | None = None
    taxable: bool | None = None
    calculation_type: str | None = None
    default_amount: Decimal | None = None


class PayItemRead(PayItemBase):
    id: int

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_employees: int
    active_employees: int
    department_count: int
    pay_group_count: int
    pay_run_count: int
    leave_requests_pending: int
    turnover_rate: float = 0
    total_payroll: float = 0


class AttendanceMonthSummaryBase(BaseModel):
    emp_id: int
    year_month: str
    planned_hours: Decimal = Decimal("0")
    worked_hours: Decimal = Decimal("0")
    overtime_hours: Decimal = Decimal("0")
    night_hours: Decimal = Decimal("0")
    holiday_hours: Decimal = Decimal("0")
    late_count: int = 0
    early_leave_count: int = 0
    absence_count: int = 0
    is_locked: bool = False


class AttendanceMonthSummaryRead(AttendanceMonthSummaryBase):
    id: int

    class Config:
        from_attributes = True


class PayGroupBase(BaseModel):
    code: str
    name: str
    pay_cycle: str = "MONTHLY"
    cutoff_day: int = 25
    pay_day: int = 10


class PayGroupCreate(PayGroupBase):
    pass


class PayGroupUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    pay_cycle: str | None = None
    cutoff_day: int | None = None
    pay_day: int | None = None


class PayGroupRead(PayGroupBase):
    id: int

    class Config:
        from_attributes = True


class PayRunBase(BaseModel):
    pay_group_id: int
    year_month: str
    run_type: str = "REGULAR"


class PayRunCreate(PayRunBase):
    pass


class PayRunRead(PayRunBase):
    id: int
    status: str
    calculated_at: datetime | None
    paid_at: datetime | None

    class Config:
        from_attributes = True


class PayResultBase(BaseModel):
    pay_run_id: int
    emp_id: int
    gross_amount: Decimal = Decimal("0")
    deduct_amount: Decimal = Decimal("0")
    net_amount: Decimal = Decimal("0")
    currency: str = "KRW"


class PayResultRead(PayResultBase):
    id: int
    status: str

    class Config:
        from_attributes = True


class PermissionRequestCreate(BaseModel):
    requested_role: str
    reason: str | None = None
    target_user_id: int | None = None


class PermissionRequestRead(BaseModel):
    id: int
    requester_user_id: int
    target_user_id: int
    requested_role: str
    status: str
    reason: str | None
    created_at: datetime
    decided_at: datetime | None = None
    decided_by_user_id: int | None = None

    class Config:
        from_attributes = True


class EvaluationPlanBase(BaseModel):
    name: str
    year: int
    status: str = "OPEN"
    start_date: date | None = None
    end_date: date | None = None


class EvaluationPlanCreate(EvaluationPlanBase):
    pass


class EvaluationPlanUpdate(BaseModel):
    name: str | None = None
    year: int | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class EvaluationPlanRead(EvaluationPlanBase):
    id: int

    class Config:
        from_attributes = True


class EvaluationItemBase(BaseModel):
    name: str
    weight: float = 0
    category: str | None = None


class EvaluationItemCreate(EvaluationItemBase):
    plan_id: int


class EvaluationItemUpdate(BaseModel):
    name: str | None = None
    weight: float | None = None
    category: str | None = None


class EvaluationItemRead(EvaluationItemBase):
    id: int
    plan_id: int

    class Config:
        from_attributes = True


class EvaluationScoreInput(BaseModel):
    item_id: int
    score: float
    comment: str | None = None


class EvaluationItemWithMyScore(EvaluationItemRead):
    my_score: float | None = None
    my_comment: str | None = None


class MyEvaluationUpsertRequest(BaseModel):
    plan_id: int
    scores: list[EvaluationScoreInput]


class TeamEvaluationUpsertRequest(BaseModel):
    plan_id: int
    target_emp_id: int
    scores: list[EvaluationScoreInput]


class GradePolicyBase(BaseModel):
    min_score: float
    max_score: float
    grade: str
    is_promotion_candidate: bool = False


class GradePolicyCreate(GradePolicyBase):
    pass


class GradePolicyRead(GradePolicyBase):
    id: int
    plan_id: int

    class Config:
        from_attributes = True


class EvaluationResultCreate(BaseModel):
    plan_id: int
    score: Decimal
    comment: str | None = None


class EvaluationResultRead(BaseModel):
    id: int
    plan_id: int
    emp_id: int
    evaluator_emp_id: int | None = None
    score: Decimal
    comment: str | None = None
    grade: str | None = None
    is_promotion_candidate: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrainingCourseBase(BaseModel):
    code: str
    name: str
    category: str | None = None
    is_active: bool = True


class TrainingCourseCreate(TrainingCourseBase):
    pass


class TrainingCourseUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    is_active: bool | None = None


class TrainingCourseRead(TrainingCourseBase):
    id: int

    class Config:
        from_attributes = True


class TrainingSessionBase(BaseModel):
    course_id: int
    title: str
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None


class TrainingSessionCreate(TrainingSessionBase):
    pass


class TrainingSessionUpdate(BaseModel):
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None


class TrainingSessionRead(TrainingSessionBase):
    id: int

    class Config:
        from_attributes = True


class TrainingEnrollmentCreate(BaseModel):
    session_id: int


class TrainingEnrollmentRead(BaseModel):
    id: int
    session_id: int
    emp_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnrollmentStatusUpdate(BaseModel):
    status: str


class EmployeeJobHistoryRead(BaseModel):
    id: int
    emp_id: int
    from_dept_id: int | None
    to_dept_id: int | None
    change_date: date
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeStatusHistoryRead(BaseModel):
    id: int
    emp_id: int
    from_status: str | None
    to_status: str
    change_date: date
    reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class BenefitPolicyBase(BaseModel):
    code: str
    name: str
    policy_type: str = "POINT"
    default_points: float = 0
    is_active: bool = True


class BenefitPolicyCreate(BenefitPolicyBase):
    pass


class BenefitPolicyRead(BenefitPolicyBase):
    id: int

    class Config:
        from_attributes = True


class PointBalanceRead(BaseModel):
    id: int
    emp_id: int
    policy_id: int
    balance: float
    year: int

    class Config:
        from_attributes = True


class PointBalanceCreate(BaseModel):
    emp_id: int
    policy_id: int
    year: int
    initial_balance: float = 0


class PointTransactionCreate(BaseModel):
    balance_id: int
    amount: float
    txn_type: str  # GRANT, USE, EXPIRE, ADJUST
    memo: str | None = None


class PointTransactionRead(BaseModel):
    id: int
    balance_id: int
    amount: float
    txn_type: str
    memo: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CodeGroupBase(BaseModel):
    code: str
    name: str


class CodeGroupRead(CodeGroupBase):
    id: int

    class Config:
        from_attributes = True


class CodeBase(BaseModel):
    code: str
    name: str
    sort_order: int = 0
    is_active: bool = True


class CodeRead(CodeBase):
    id: int
    group_id: int

    class Config:
        from_attributes = True


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    old_value: str | None
    new_value: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TimeLogCreate(BaseModel):
    emp_id: int | None = None
    log_datetime: datetime
    log_type: str  # IN / OUT
    source: str = "WEB"


class TimeLogRead(BaseModel):
    id: int
    emp_id: int
    log_datetime: datetime
    log_type: str
    source: str

    class Config:
        from_attributes = True

