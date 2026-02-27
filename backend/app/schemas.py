from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class DepartmentBase(BaseModel):
    code: str
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentRead(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    emp_no: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    hire_date: date
    status: str = "ACTIVE"
    dept_id: int | None = None
    pay_group_id: int | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase):
    id: int

    class Config:
        from_attributes = True


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

