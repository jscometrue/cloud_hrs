from datetime import date, datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import auth, database, models, schemas

database.init_db()

app = FastAPI(
    title="JSCORP HR System API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_sample_data(db: Session) -> None:
    if db.query(models.Department).count() > 0:
        return

    dept = models.Department(code="HQ", name="Headquarters")
    pay_group = models.PayGroup(code="JSCORP_MONTHLY", name="JSCORP Monthly")
    db.add_all([dept, pay_group])
    db.flush()

    emp = models.Employee(
        emp_no="E0001",
        first_name="Jin",
        last_name="Kim",
        email="jin.kim@jscorp.com",
        dept_id=dept.id,
        pay_group_id=pay_group.id,
        hire_date=date.today(),
    )
    db.add(emp)
    db.flush()

    summary = models.AttendanceMonthSummary(
        emp_id=emp.id,
        year_month=date.today().strftime("%Y%m"),
        planned_hours=160,
        worked_hours=162,
        overtime_hours=2,
        late_count=0,
        early_leave_count=0,
        absence_count=0,
    )
    db.add(summary)

    pay_run = models.PayRun(
        pay_group_id=pay_group.id,
        year_month=date.today().strftime("%Y%m"),
        run_type="REGULAR",
        status="CALCULATED",
    )
    db.add(pay_run)
    db.flush()

    pay_result = models.PayResult(
        pay_run_id=pay_run.id,
        emp_id=emp.id,
        gross_amount=5_000_000,
        deduct_amount=1_000_000,
        net_amount=4_000_000,
    )
    db.add(pay_result)

    if db.query(models.WorkType).count() == 0:
        wt = models.WorkType(
            code="DAY",
            name="Day shift",
            start_time="09:00",
            end_time="18:00",
            break_minutes=60,
        )
        db.add(wt)
    if db.query(models.PayItem).count() == 0:
        for code, name, itype, amt in [
            ("BASE", "Base salary", "EARNING", 0),
            ("OT", "Overtime", "EARNING", 0),
            ("TAX", "Income tax", "DEDUCTION", 0),
            ("INS", "Insurance", "DEDUCTION", 0),
        ]:
            db.add(
                models.PayItem(
                    code=code,
                    name=name,
                    item_type=itype,
                    calculation_type="FIXED",
                    default_amount=amt,
                )
            )

    db.commit()


def seed_user(db: Session) -> None:
    if db.query(models.User).filter(models.User.username == "admin").first():
        return
    user = models.User(
        username="admin",
        password_hash=auth.get_password_hash("admin123"),
    )
    db.add(user)
    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    db = database.SessionLocal()
    try:
        seed_sample_data(db)
        seed_user(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "JSCORP HR"}


@app.post("/api/auth/login", response_model=schemas.Token)
def login(
    payload: schemas.LoginRequest, db: Session = Depends(database.get_db)
) -> schemas.Token:
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    return schemas.Token(access_token=auth.create_access_token(user.username))


# ---- Departments (Organization) ----
@app.get("/api/departments", response_model=list[schemas.DepartmentRead])
def list_departments(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.DepartmentRead]:
    return db.query(models.Department).order_by(models.Department.code).all()


@app.get("/api/departments/{dept_id}", response_model=schemas.DepartmentRead)
def get_department(
    dept_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.DepartmentRead:
    dept = db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@app.post("/api/departments", response_model=schemas.DepartmentRead, status_code=201)
def create_department(
    payload: schemas.DepartmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.DepartmentRead:
    if db.query(models.Department).filter(models.Department.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Department code already exists")
    dept = models.Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@app.patch("/api/departments/{dept_id}", response_model=schemas.DepartmentRead)
def update_department(
    dept_id: int,
    payload: schemas.DepartmentUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.DepartmentRead:
    dept = db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


@app.delete("/api/departments/{dept_id}", status_code=204)
def delete_department(
    dept_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> None:
    dept = db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    if db.query(models.Employee).filter(models.Employee.dept_id == dept_id).first():
        raise HTTPException(status_code=400, detail="Department has employees")
    db.delete(dept)
    db.commit()


# ---- Employees ----
@app.get("/api/employees", response_model=list[schemas.EmployeeRead])
def list_employees(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.EmployeeRead]:
    employees = db.query(models.Employee).order_by(models.Employee.emp_no).all()
    return employees


@app.get("/api/employees/{emp_id}", response_model=schemas.EmployeeRead)
def get_employee(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EmployeeRead:
    emp = db.get(models.Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.post("/api/employees", response_model=schemas.EmployeeRead, status_code=201)
def create_employee(
    payload: schemas.EmployeeCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EmployeeRead:
    exists = (
        db.query(models.Employee)
        .filter(
            (models.Employee.emp_no == payload.emp_no)
            | (models.Employee.email == payload.email)
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Employee already exists")
    emp = models.Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@app.patch("/api/employees/{emp_id}", response_model=schemas.EmployeeRead)
def update_employee(
    emp_id: int,
    payload: schemas.EmployeeUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EmployeeRead:
    emp = db.get(models.Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(emp, k, v)
    db.commit()
    db.refresh(emp)
    return emp


@app.delete("/api/employees/{emp_id}", status_code=204)
def delete_employee(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> None:
    emp = db.get(models.Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(emp)
    db.commit()


# ---- Pay Groups (Organization) ----
@app.get("/api/payroll/pay-groups", response_model=list[schemas.PayGroupRead])
def list_pay_groups(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PayGroupRead]:
    return db.query(models.PayGroup).order_by(models.PayGroup.code).all()


@app.get("/api/payroll/pay-groups/{pg_id}", response_model=schemas.PayGroupRead)
def get_pay_group(
    pg_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayGroupRead:
    pg = db.get(models.PayGroup, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Pay group not found")
    return pg


@app.post("/api/payroll/pay-groups", response_model=schemas.PayGroupRead, status_code=201)
def create_pay_group(
    payload: schemas.PayGroupCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayGroupRead:
    if db.query(models.PayGroup).filter(models.PayGroup.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Pay group code already exists")
    pg = models.PayGroup(**payload.model_dump())
    db.add(pg)
    db.commit()
    db.refresh(pg)
    return pg


@app.patch("/api/payroll/pay-groups/{pg_id}", response_model=schemas.PayGroupRead)
def update_pay_group(
    pg_id: int,
    payload: schemas.PayGroupUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayGroupRead:
    pg = db.get(models.PayGroup, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Pay group not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(pg, k, v)
    db.commit()
    db.refresh(pg)
    return pg


@app.delete("/api/payroll/pay-groups/{pg_id}", status_code=204)
def delete_pay_group(
    pg_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> None:
    pg = db.get(models.PayGroup, pg_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Pay group not found")
    if db.query(models.Employee).filter(models.Employee.pay_group_id == pg_id).first():
        raise HTTPException(status_code=400, detail="Pay group has employees")
    db.delete(pg)
    db.commit()


# ---- Pay Items ----
@app.get("/api/payroll/pay-items", response_model=list[schemas.PayItemRead])
def list_pay_items(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PayItemRead]:
    return db.query(models.PayItem).order_by(models.PayItem.code).all()


@app.post("/api/payroll/pay-items", response_model=schemas.PayItemRead, status_code=201)
def create_pay_item(
    payload: schemas.PayItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayItemRead:
    if db.query(models.PayItem).filter(models.PayItem.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Pay item code already exists")
    pi = models.PayItem(**payload.model_dump())
    db.add(pi)
    db.commit()
    db.refresh(pi)
    return pi


@app.get("/api/payroll/pay-items/{pi_id}", response_model=schemas.PayItemRead)
def get_pay_item(
    pi_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayItemRead:
    pi = db.get(models.PayItem, pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Pay item not found")
    return pi


@app.patch("/api/payroll/pay-items/{pi_id}", response_model=schemas.PayItemRead)
def update_pay_item(
    pi_id: int,
    payload: schemas.PayItemUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayItemRead:
    pi = db.get(models.PayItem, pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Pay item not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(pi, k, v)
    db.commit()
    db.refresh(pi)
    return pi


@app.delete("/api/payroll/pay-items/{pi_id}", status_code=204)
def delete_pay_item(
    pi_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> None:
    pi = db.get(models.PayItem, pi_id)
    if not pi:
        raise HTTPException(status_code=404, detail="Pay item not found")
    db.delete(pi)
    db.commit()


# ---- Attendance ----
@app.get(
    "/api/attendance/monthly",
    response_model=list[schemas.AttendanceMonthSummaryRead],
)
def list_attendance_monthly(
    year_month: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.AttendanceMonthSummaryRead]:
    summaries = (
        db.query(models.AttendanceMonthSummary)
        .filter(models.AttendanceMonthSummary.year_month == year_month)
        .all()
    )
    return summaries


@app.get("/api/attendance/work-types", response_model=list[schemas.WorkTypeRead])
def list_work_types(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.WorkTypeRead]:
    return db.query(models.WorkType).order_by(models.WorkType.code).all()


@app.post("/api/attendance/work-types", response_model=schemas.WorkTypeRead, status_code=201)
def create_work_type(
    payload: schemas.WorkTypeCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.WorkTypeRead:
    if db.query(models.WorkType).filter(models.WorkType.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Work type code already exists")
    wt = models.WorkType(**payload.model_dump())
    db.add(wt)
    db.commit()
    db.refresh(wt)
    return wt


@app.patch("/api/attendance/work-types/{wt_id}", response_model=schemas.WorkTypeRead)
def update_work_type(
    wt_id: int,
    payload: schemas.WorkTypeUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.WorkTypeRead:
    wt = db.get(models.WorkType, wt_id)
    if not wt:
        raise HTTPException(status_code=404, detail="Work type not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(wt, k, v)
    db.commit()
    db.refresh(wt)
    return wt


@app.delete("/api/attendance/work-types/{wt_id}", status_code=204)
def delete_work_type(
    wt_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> None:
    wt = db.get(models.WorkType, wt_id)
    if not wt:
        raise HTTPException(status_code=404, detail="Work type not found")
    db.delete(wt)
    db.commit()


@app.get("/api/attendance/leave-requests", response_model=list[schemas.LeaveRequestRead])
def list_leave_requests(
    emp_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.LeaveRequestRead]:
    q = db.query(models.LeaveRequest)
    if emp_id is not None:
        q = q.filter(models.LeaveRequest.emp_id == emp_id)
    if status is not None:
        q = q.filter(models.LeaveRequest.status == status)
    return q.order_by(models.LeaveRequest.start_datetime.desc()).all()


@app.post("/api/attendance/leave-requests", response_model=schemas.LeaveRequestRead, status_code=201)
def create_leave_request(
    payload: schemas.LeaveRequestCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.LeaveRequestRead:
    if not db.get(models.Employee, payload.emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    lr = models.LeaveRequest(
        emp_id=payload.emp_id,
        leave_type=payload.leave_type,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        hours=float(payload.hours),
        reason=payload.reason,
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return lr


@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.DashboardStats:
    total = db.query(models.Employee).count()
    active = db.query(models.Employee).filter(models.Employee.status == "ACTIVE").count()
    dept_count = db.query(models.Department).count()
    pg_count = db.query(models.PayGroup).count()
    run_count = db.query(models.PayRun).count()
    leave_pending = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.status == "REQUESTED"
    ).count()
    return schemas.DashboardStats(
        total_employees=total,
        active_employees=active,
        department_count=dept_count,
        pay_group_count=pg_count,
        pay_run_count=run_count,
        leave_requests_pending=leave_pending,
    )


# ---- Payroll runs ----
@app.get("/api/payroll/runs", response_model=list[schemas.PayRunRead])
def list_pay_runs(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PayRunRead]:
    runs = db.query(models.PayRun).order_by(
        models.PayRun.year_month.desc(), models.PayRun.id.desc()
    )
    return list(runs)


@app.post("/api/payroll/runs", response_model=schemas.PayRunRead, status_code=201)
def create_pay_run(
    payload: schemas.PayRunCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PayRunRead:
    pg = db.get(models.PayGroup, payload.pay_group_id)
    if not pg:
        raise HTTPException(status_code=404, detail="Pay group not found")
    run = models.PayRun(**payload.model_dump())
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.get(
    "/api/payroll/runs/{run_id}/results",
    response_model=list[schemas.PayResultRead],
)
def list_pay_results_by_run(
    run_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PayResultRead]:
    run = db.get(models.PayRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    results = db.query(models.PayResult).filter(models.PayResult.pay_run_id == run_id)
    return list(results)

