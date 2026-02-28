from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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

