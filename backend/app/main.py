from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import database, models, schemas

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

    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    db = database.SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "JSCORP HR"}


@app.get("/api/employees", response_model=list[schemas.EmployeeRead])
def list_employees(db: Session = Depends(database.get_db)) -> list[schemas.EmployeeRead]:
    employees = db.query(models.Employee).order_by(models.Employee.emp_no).all()
    return employees


@app.post("/api/employees", response_model=schemas.EmployeeRead, status_code=201)
def create_employee(
    payload: schemas.EmployeeCreate, db: Session = Depends(database.get_db)
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


@app.get(
    "/api/attendance/monthly",
    response_model=list[schemas.AttendanceMonthSummaryRead],
)
def list_attendance_monthly(
    year_month: str, db: Session = Depends(database.get_db)
) -> list[schemas.AttendanceMonthSummaryRead]:
    summaries = (
        db.query(models.AttendanceMonthSummary)
        .filter(models.AttendanceMonthSummary.year_month == year_month)
        .all()
    )
    return summaries


@app.get("/api/payroll/runs", response_model=list[schemas.PayRunRead])
def list_pay_runs(db: Session = Depends(database.get_db)) -> list[schemas.PayRunRead]:
    runs = db.query(models.PayRun).order_by(
        models.PayRun.year_month.desc(), models.PayRun.id.desc()
    )
    return list(runs)


@app.get(
    "/api/payroll/runs/{run_id}/results",
    response_model=list[schemas.PayResultRead],
)
def list_pay_results_by_run(
    run_id: int, db: Session = Depends(database.get_db)
) -> list[schemas.PayResultRead]:
    run = db.get(models.PayRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    results = db.query(models.PayResult).filter(models.PayResult.pay_run_id == run_id)
    return list(results)

