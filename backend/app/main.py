import secrets
from datetime import date, datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import auth, database, models, schemas

database.init_db()

REQUESTABLE_ROLES = {"MANAGER", "HR_ADMIN", "PAYROLL_ADMIN"}

app = FastAPI(
    title="JSCORP HR System API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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

    if db.query(models.BenefitPolicy).count() == 0:
        for code, name, ptype, pts in [
            ("WELFARE_POINT", "복지포인트", "POINT", 100000),
            ("MEAL", "식대", "MEAL", 0),
        ]:
            db.add(
                models.BenefitPolicy(
                    code=code,
                    name=name,
                    policy_type=ptype,
                    default_points=pts,
                    is_active=True,
                )
            )

    if db.query(models.CodeGroup).count() == 0:
        cg_leave = models.CodeGroup(code="LEAVE_TYPE", name="휴가유형")
        cg_status = models.CodeGroup(code="EMP_STATUS", name="직원상태")
        db.add_all([cg_leave, cg_status])
        db.flush()
        for group_id, code, name, order in [
            (cg_leave.id, "ANNUAL", "연차", 1),
            (cg_leave.id, "SICK", "병가", 2),
            (cg_leave.id, "SPECIAL", "특별휴가", 3),
            (cg_status.id, "ACTIVE", "재직", 1),
            (cg_status.id, "INACTIVE", "휴직", 2),
            (cg_status.id, "TERMINATED", "퇴직", 3),
        ]:
            db.add(models.Code(group_id=group_id, code=code, name=name, sort_order=order))

    if db.query(models.EvaluationPlan).count() == 0:
        ep = models.EvaluationPlan(
            name="2025 연간 평가",
            year=2025,
            status="OPEN",
        )
        db.add(ep)
        db.flush()
        for name, weight, cat in [
            ("업무성과", 40, "SELF"),
            ("역량", 30, "SELF"),
            ("협업", 30, "SELF"),
        ]:
            db.add(models.EvaluationItem(plan_id=ep.id, name=name, weight=weight, category=cat))
        for min_s, max_s, grade, promo in [
            (90, 100, "S", True),
            (80, 89.99, "A", False),
            (70, 79.99, "B", False),
            (60, 69.99, "C", False),
            (0, 59.99, "D", False),
        ]:
            db.add(models.GradePolicy(plan_id=ep.id, min_score=min_s, max_score=max_s, grade=grade, is_promotion_candidate=promo))

    db.commit()


def seed_user(db: Session) -> None:
    def ensure_user(username: str, password: str, email_verified: bool = True, role: str = "EMPLOYEE") -> None:
        existing = db.query(models.User).filter(models.User.username == username).first()
        h = auth.get_password_hash(password)
        if existing:
            existing.password_hash = h
            if hasattr(existing, "email_verified"):
                existing.email_verified = email_verified
            if hasattr(existing, "role"):
                existing.role = role
            db.commit()
            return
        u = models.User(
            username=username,
            password_hash=h,
            email_verified=email_verified,
            role=role,
        )
        db.add(u)
        db.flush()

    ensure_user("admin", "admin123", email_verified=True, role="ADMIN")
    ensure_user("hradmin", "hr123", email_verified=True, role="HR_ADMIN")
    ensure_user("manager1", "mgr123", email_verified=True, role="MANAGER")
    ensure_user("sample1", "sample123", email_verified=True, role="EMPLOYEE")
    ensure_user("sample2", "sample123", email_verified=True, role="EMPLOYEE")
    ensure_user("sample3", "sample123", email_verified=True, role="EMPLOYEE")
    db.commit()


@app.on_event("startup")
def on_startup() -> None:
    db = database.SessionLocal()
    try:
        seed_sample_data(db)
        seed_user(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "JSCORP HR"}


@app.post("/api/auth/login", response_model=schemas.Token)
def login(
    payload: schemas.LoginRequest, db: Session = Depends(database.get_db)
) -> schemas.Token:
    from sqlalchemy import func

    username = (payload.username or "").strip()
    password = payload.password if payload.password is not None else ""
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    user = (
        db.query(models.User)
        .filter(func.lower(models.User.username) == func.lower(username))
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    if getattr(user, "email", None) and not getattr(user, "email_verified", True):
        raise HTTPException(status_code=403, detail="Verify your email first")
    if not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return schemas.Token(access_token=auth.create_access_token(user.username))


@app.post("/api/auth/request-verification")
def request_verification(
    payload: schemas.RequestVerificationRequest,
    db: Session = Depends(database.get_db),
) -> dict:
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    db.commit()
    return {"message": "Verification link sent", "verification_url": f"/verify-email?token={token}"}


@app.get("/api/auth/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(database.get_db),
) -> dict:
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.email_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified. You can now log in."}


@app.post("/api/auth/request-password-reset")
def request_password_reset(
    payload: schemas.RequestPasswordResetRequest,
    db: Session = Depends(database.get_db),
) -> dict:
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()
    return {"message": "Reset link sent", "token": token}


@app.post("/api/auth/reset-password-by-token")
def reset_password_by_token(
    payload: schemas.ResetPasswordByTokenRequest,
    db: Session = Depends(database.get_db),
) -> dict:
    user = db.query(models.User).filter(models.User.reset_token == payload.token).first()
    if not user or (user.reset_token_expires and user.reset_token_expires < datetime.now(timezone.utc)):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.password_hash = auth.get_password_hash(payload.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return {"message": "Password reset. You can now log in."}


@app.get("/api/auth/me", response_model=schemas.UserRead)
def get_me(
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.UserRead:
    return current_user


@app.post("/api/auth/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> dict[str, str]:
    if not auth.verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is wrong")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    user.password_hash = auth.get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password updated"}


@app.get("/api/users", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin),
) -> list[schemas.UserRead]:
    return db.query(models.User).order_by(models.User.username).all()


@app.post("/api/users", response_model=schemas.UserRead, status_code=201)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin),
) -> schemas.UserRead:
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = models.User(
        username=payload.username,
        password_hash=auth.get_password_hash(payload.password),
        email=payload.email,
        email_verified=payload.email_verified,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.patch("/api/users/{user_id}/password")
def reset_user_password(
    user_id: int,
    payload: schemas.ResetPasswordRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin),
) -> dict[str, str]:
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = auth.get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Password reset"}


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
    # ADMIN / HR_ADMIN 은 전체 조회
    if getattr(current_user, "role", None) in ("ADMIN", "HR_ADMIN"):
        return db.query(models.Employee).order_by(models.Employee.emp_no).all()

    # 나머지 역할은 기본적으로 자기 자신 또는 본인 조직만 조회
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []

    q = db.query(models.Employee)
    if getattr(current_user, "role", None) == "MANAGER":
        # MANAGER 는 같은 부서(dept_id) 직원 조회
        q = q.filter(models.Employee.dept_id == me_emp.dept_id)
    else:
        # 일반 직원은 자기 자신만
        q = q.filter(models.Employee.id == me_emp.id)
    return q.order_by(models.Employee.emp_no).all()


@app.get("/api/employees/{emp_id}", response_model=schemas.EmployeeRead)
def get_employee(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EmployeeRead:
    emp = db.get(models.Employee, emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # ADMIN / HR_ADMIN 은 상세 조회 허용
    if getattr(current_user, "role", None) in ("ADMIN", "HR_ADMIN"):
        return emp

    # MANAGER / EMPLOYEE 는 스코프 체크
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if getattr(current_user, "role", None) == "MANAGER":
        # 같은 부서이거나 본인인 경우만 허용
        if emp.dept_id != me_emp.dept_id and emp.id != me_emp.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    else:
        # 일반 직원은 자기 자신만
        if emp.id != me_emp.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return emp


@app.get(
    "/api/employees/{emp_id}/job-history",
    response_model=list[schemas.EmployeeJobHistoryRead],
)
def get_employee_job_history(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> list[schemas.EmployeeJobHistoryRead]:
    if not db.get(models.Employee, emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return (
        db.query(models.EmployeeJobHistory)
        .filter(models.EmployeeJobHistory.emp_id == emp_id)
        .order_by(models.EmployeeJobHistory.change_date.desc(), models.EmployeeJobHistory.id.desc())
        .all()
    )


@app.get(
    "/api/employees/{emp_id}/status-history",
    response_model=list[schemas.EmployeeStatusHistoryRead],
)
def get_employee_status_history(
    emp_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> list[schemas.EmployeeStatusHistoryRead]:
    if not db.get(models.Employee, emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return (
        db.query(models.EmployeeStatusHistory)
        .filter(models.EmployeeStatusHistory.emp_id == emp_id)
        .order_by(models.EmployeeStatusHistory.change_date.desc(), models.EmployeeStatusHistory.id.desc())
        .all()
    )


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
    db.flush()

    # 직원 생성 시 기본 로그인 계정을 emp_no 기반으로 자동 생성
    username = payload.emp_no
    existing_user = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if not existing_user:
        user = models.User(
            username=username,
            password_hash=auth.get_password_hash(username),
            email=payload.email,
            email_verified=False,
            role="EMPLOYEE",
        )
        db.add(user)
        db.flush()
        emp.user_id = user.id

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

    old_dept_id = emp.dept_id
    old_status = emp.status

    for k, v in data.items():
        setattr(emp, k, v)

    # 인사이동 이력 기록 (부서 변경 시)
    if "dept_id" in data and data["dept_id"] != old_dept_id:
        hist = models.EmployeeJobHistory(
            emp_id=emp.id,
            from_dept_id=old_dept_id,
            to_dept_id=data["dept_id"],
        )
        db.add(hist)

    # 상태 변경 이력 기록 + 계정 잠금
    if "status" in data and data["status"] != old_status:
        sh = models.EmployeeStatusHistory(
            emp_id=emp.id,
            from_status=old_status,
            to_status=data["status"],
        )
        db.add(sh)
        if data["status"] != "ACTIVE" and emp.user_id:
            user = db.get(models.User, emp.user_id)
            if user:
                user.is_active = False

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

    # 삭제 시 연계된 사용자 계정은 잠금 처리만 수행
    if emp.user_id:
        user = db.get(models.User, emp.user_id)
        if user:
            user.is_active = False

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
    q = db.query(models.AttendanceMonthSummary).filter(
        models.AttendanceMonthSummary.year_month == year_month
    )

    # ADMIN / HR_ADMIN 은 전체 월 근태 요약 조회
    role = getattr(current_user, "role", None)
    if role in ("ADMIN", "HR_ADMIN"):
        return q.all()

    # 나머지 역할은 Employee 스코프를 기준으로 제한
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []

    emp_q = db.query(models.Employee.id)
    if role == "MANAGER":
        emp_q = emp_q.filter(models.Employee.dept_id == me_emp.dept_id)
    else:
        emp_q = emp_q.filter(models.Employee.id == me_emp.id)

    visible_emp_ids = [row[0] for row in emp_q.all()]
    if not visible_emp_ids:
        return []

    q = q.filter(models.AttendanceMonthSummary.emp_id.in_(visible_emp_ids))
    return q.all()


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
    role = getattr(current_user, "role", None)
    q = db.query(models.LeaveRequest)

    if emp_id is not None:
        q = q.filter(models.LeaveRequest.emp_id == emp_id)
    if status is not None:
        q = q.filter(models.LeaveRequest.status == status)

    # ADMIN / HR_ADMIN 은 필터 조건만 적용
    if role in ("ADMIN", "HR_ADMIN"):
        return q.order_by(models.LeaveRequest.start_datetime.desc()).all()

    # 나머지 역할은 Employee 스코프 기준으로 제한
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []

    emp_q = db.query(models.Employee.id)
    if role == "MANAGER":
        emp_q = emp_q.filter(models.Employee.dept_id == me_emp.dept_id)
    else:
        emp_q = emp_q.filter(models.Employee.id == me_emp.id)

    visible_emp_ids = [row[0] for row in emp_q.all()]
    if not visible_emp_ids:
        return []

    q = q.filter(models.LeaveRequest.emp_id.in_(visible_emp_ids))
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


@app.post(
    "/api/attendance/leave-requests/{leave_id}/approve",
    response_model=schemas.LeaveRequestRead,
)
def approve_leave_request(
    leave_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN", "MANAGER")),
) -> schemas.LeaveRequestRead:
    lr = db.get(models.LeaveRequest, leave_id)
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.status != "REQUESTED":
        raise HTTPException(status_code=400, detail="Leave request is not pending")

    # MANAGER 인 경우, 본인 부서 직원만 승인 가능
    role = getattr(current_user, "role", None)
    if role == "MANAGER":
        me_emp = (
            db.query(models.Employee)
            .filter(models.Employee.user_id == current_user.id)
            .first()
        )
        if not me_emp:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        target_emp = db.get(models.Employee, lr.emp_id)
        if not target_emp or target_emp.dept_id != me_emp.dept_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    approver_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )

    lr.status = "APPROVED"
    lr.approved_at = datetime.now(timezone.utc)
    lr.approver_emp_id = approver_emp.id if approver_emp else None
    db.commit()
    db.refresh(lr)
    return lr


@app.post(
    "/api/attendance/leave-requests/{leave_id}/reject",
    response_model=schemas.LeaveRequestRead,
)
def reject_leave_request(
    leave_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN", "MANAGER")),
) -> schemas.LeaveRequestRead:
    lr = db.get(models.LeaveRequest, leave_id)
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.status != "REQUESTED":
        raise HTTPException(status_code=400, detail="Leave request is not pending")

    role = getattr(current_user, "role", None)
    if role == "MANAGER":
        me_emp = (
            db.query(models.Employee)
            .filter(models.Employee.user_id == current_user.id)
            .first()
        )
        if not me_emp:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        target_emp = db.get(models.Employee, lr.emp_id)
        if not target_emp or target_emp.dept_id != me_emp.dept_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    approver_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )

    lr.status = "REJECTED"
    lr.approved_at = datetime.now(timezone.utc)
    lr.approver_emp_id = approver_emp.id if approver_emp else None
    db.commit()
    db.refresh(lr)
    return lr


@app.post("/api/attendance/close-month")
def close_attendance_month(
    year_month: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> dict[str, int]:
    q = db.query(models.AttendanceMonthSummary).filter(
        models.AttendanceMonthSummary.year_month == year_month
    )
    updated = q.update({models.AttendanceMonthSummary.is_locked: True})
    db.commit()
    return {"locked_rows": updated}


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
    turnover_rate = (total - active) / total if total > 0 else 0.0
    total_payroll = sum(
        float(r.net_amount) for r in db.query(models.PayResult).all()
    )
    return schemas.DashboardStats(
        total_employees=total,
        active_employees=active,
        department_count=dept_count,
        pay_group_count=pg_count,
        pay_run_count=run_count,
        leave_requests_pending=leave_pending,
        turnover_rate=round(turnover_rate * 100, 1),
        total_payroll=total_payroll,
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

    role = getattr(current_user, "role", None)
    q = db.query(models.PayResult).filter(models.PayResult.pay_run_id == run_id)

    # ADMIN / HR_ADMIN 은 전체 결과 조회
    if role in ("ADMIN", "HR_ADMIN"):
        return list(q)

    # 나머지 역할은 Employee 스코프 기준으로 제한
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []

    emp_q = db.query(models.Employee.id)
    if role == "MANAGER":
        emp_q = emp_q.filter(models.Employee.dept_id == me_emp.dept_id)
    else:
        emp_q = emp_q.filter(models.Employee.id == me_emp.id)

    visible_emp_ids = [row[0] for row in emp_q.all()]
    if not visible_emp_ids:
        return []

    q = q.filter(models.PayResult.emp_id.in_(visible_emp_ids))
    return list(q)


@app.post("/api/payroll/runs/{run_id}/calculate")
def calculate_payroll_run(
    run_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> dict[str, int]:
    run = db.get(models.PayRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    # 같은 급여그룹의 ACTIVE 직원 대상
    employees = (
        db.query(models.Employee)
        .filter(
            models.Employee.pay_group_id == run.pay_group_id,
            models.Employee.status == "ACTIVE",
        )
        .all()
    )

    created = 0
    updated = 0
    for emp in employees:
        summary = (
            db.query(models.AttendanceMonthSummary)
            .filter(
                models.AttendanceMonthSummary.emp_id == emp.id,
                models.AttendanceMonthSummary.year_month == run.year_month,
            )
            .first()
        )
        worked_hours = float(summary.worked_hours) if summary else 0.0

        # 매우 단순한 예시 계산 로직 (시급 20,000원 가정)
        gross = worked_hours * 20000
        deduct = gross * 0.1  # 10% 공제 가정
        net = gross - deduct

        pr = (
            db.query(models.PayResult)
            .filter(
                models.PayResult.pay_run_id == run.id,
                models.PayResult.emp_id == emp.id,
            )
            .first()
        )
        if pr:
            pr.gross_amount = gross
            pr.deduct_amount = deduct
            pr.net_amount = net
            pr.status = "CALCULATED"
            updated += 1
        else:
            pr = models.PayResult(
                pay_run_id=run.id,
                emp_id=emp.id,
                gross_amount=gross,
                deduct_amount=deduct,
                net_amount=net,
                status="CALCULATED",
            )
            db.add(pr)
            created += 1

    run.status = "CALCULATED"
    run.calculated_at = datetime.now(timezone.utc)
    db.commit()
    return {"created": created, "updated": updated}


# ---- Permission requests ----
@app.post(
    "/api/permissions/requests",
    response_model=schemas.PermissionRequestRead,
    status_code=201,
)
def create_permission_request(
    payload: schemas.PermissionRequestCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.PermissionRequestRead:
    requested_role = payload.requested_role
    if requested_role not in REQUESTABLE_ROLES:
        raise HTTPException(status_code=400, detail="Requested role not allowed")

    target_user_id = payload.target_user_id or current_user.id
    target_user = db.get(models.User, target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    pr = models.PermissionRequest(
        requester_user_id=current_user.id,
        target_user_id=target_user_id,
        requested_role=requested_role,
        reason=payload.reason,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr


@app.get(
    "/api/permissions/requests/mine",
    response_model=list[schemas.PermissionRequestRead],
)
def list_my_permission_requests(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PermissionRequestRead]:
    return (
        db.query(models.PermissionRequest)
        .filter(models.PermissionRequest.requester_user_id == current_user.id)
        .order_by(models.PermissionRequest.created_at.desc())
        .all()
    )


@app.get(
    "/api/permissions/requests",
    response_model=list[schemas.PermissionRequestRead],
)
def list_permission_requests(
    status: str | None = Query(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> list[schemas.PermissionRequestRead]:
    q = db.query(models.PermissionRequest)
    if status is not None:
        q = q.filter(models.PermissionRequest.status == status)
    return q.order_by(models.PermissionRequest.created_at.desc()).all()


@app.post(
    "/api/permissions/requests/{req_id}/approve",
    response_model=schemas.PermissionRequestRead,
)
def approve_permission_request(
    req_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.PermissionRequestRead:
    pr = db.get(models.PermissionRequest, req_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Request not found")
    if pr.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request is not pending")

    target_user = db.get(models.User, pr.target_user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    target_user.role = pr.requested_role
    pr.status = "APPROVED"
    pr.decided_at = datetime.now(timezone.utc)
    pr.decided_by_user_id = current_user.id
    db.commit()
    db.refresh(pr)
    return pr


@app.post(
    "/api/permissions/requests/{req_id}/reject",
    response_model=schemas.PermissionRequestRead,
)
def reject_permission_request(
    req_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.PermissionRequestRead:
    pr = db.get(models.PermissionRequest, req_id)
    if not pr:
        raise HTTPException(status_code=404, detail="Request not found")
    if pr.status != "PENDING":
        raise HTTPException(status_code=400, detail="Request is not pending")

    pr.status = "REJECTED"
    pr.decided_at = datetime.now(timezone.utc)
    pr.decided_by_user_id = current_user.id
    db.commit()
    db.refresh(pr)
    return pr


# ---- Evaluation ----
@app.get("/api/evaluations/plans", response_model=list[schemas.EvaluationPlanRead])
def list_evaluation_plans(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.EvaluationPlanRead]:
    return (
        db.query(models.EvaluationPlan)
        .order_by(models.EvaluationPlan.year.desc(), models.EvaluationPlan.id.desc())
        .all()
    )


@app.post(
    "/api/evaluations/plans",
    response_model=schemas.EvaluationPlanRead,
    status_code=201,
)
def create_evaluation_plan(
    payload: schemas.EvaluationPlanCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.EvaluationPlanRead:
    plan = models.EvaluationPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@app.patch("/api/evaluations/plans/{plan_id}", response_model=schemas.EvaluationPlanRead)
def update_evaluation_plan(
    plan_id: int,
    payload: schemas.EvaluationPlanUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.EvaluationPlanRead:
    plan = db.get(models.EvaluationPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(plan, k, v)
    db.commit()
    db.refresh(plan)
    return plan


@app.get(
    "/api/evaluations/my-result",
    response_model=schemas.EvaluationResultRead | None,
)
def get_my_evaluation_result(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EvaluationResultRead | None:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return None
    res = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == plan_id,
            models.EvaluationResult.emp_id == me_emp.id,
        )
        .first()
    )
    return res


@app.post(
    "/api/evaluations/my-result",
    response_model=schemas.EvaluationResultRead,
    status_code=201,
)
def upsert_my_evaluation_result(
    payload: schemas.EvaluationResultCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.EvaluationResultRead:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=400, detail="Employee profile not linked")

    plan = db.get(models.EvaluationPlan, payload.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status != "OPEN":
        raise HTTPException(status_code=400, detail="Plan is not open")

    res = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == payload.plan_id,
            models.EvaluationResult.emp_id == me_emp.id,
            models.EvaluationResult.evaluator_emp_id.is_(None),
        )
        .first()
    )
    if res:
        res.score = float(payload.score)
        res.comment = payload.comment
    else:
        res = models.EvaluationResult(
            plan_id=payload.plan_id,
            emp_id=me_emp.id,
            evaluator_emp_id=None,
            score=float(payload.score),
            comment=payload.comment,
        )
        db.add(res)
    db.commit()
    db.refresh(res)
    return res


@app.get(
    "/api/evaluations/plans/{plan_id}/items",
    response_model=list[schemas.EvaluationItemRead],
)
def list_evaluation_items(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.EvaluationItemRead]:
    if not db.get(models.EvaluationPlan, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    return (
        db.query(models.EvaluationItem)
        .filter(models.EvaluationItem.plan_id == plan_id)
        .order_by(models.EvaluationItem.id)
        .all()
    )


@app.post(
    "/api/evaluations/items",
    response_model=schemas.EvaluationItemRead,
    status_code=201,
)
def create_evaluation_item(
    payload: schemas.EvaluationItemCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.EvaluationItemRead:
    if not db.get(models.EvaluationPlan, payload.plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    item = models.EvaluationItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.patch(
    "/api/evaluations/items/{item_id}",
    response_model=schemas.EvaluationItemRead,
)
def update_evaluation_item(
    item_id: int,
    payload: schemas.EvaluationItemUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.EvaluationItemRead:
    item = db.get(models.EvaluationItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@app.get(
    "/api/evaluations/my-scores",
    response_model=list[schemas.EvaluationItemWithMyScore],
)
def get_my_evaluation_scores(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.EvaluationItemWithMyScore]:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []
    items = (
        db.query(models.EvaluationItem)
        .filter(models.EvaluationItem.plan_id == plan_id)
        .order_by(models.EvaluationItem.id)
        .all()
    )
    res = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == plan_id,
            models.EvaluationResult.emp_id == me_emp.id,
            models.EvaluationResult.evaluator_emp_id.is_(None),
        )
        .first()
    )
    scores_by_item = {}
    if res:
        for sc in db.query(models.EvaluationScore).filter(
            models.EvaluationScore.result_id == res.id
        ).all():
            scores_by_item[sc.item_id] = (float(sc.score), sc.comment)

    out = []
    for it in items:
        my_score, my_comment = scores_by_item.get(it.id, (None, None))
        out.append(
            schemas.EvaluationItemWithMyScore(
                id=it.id,
                plan_id=it.plan_id,
                name=it.name,
                weight=float(it.weight),
                category=it.category,
                my_score=my_score,
                my_comment=my_comment,
            )
        )
    return out


@app.post(
    "/api/evaluations/my-scores",
    response_model=list[schemas.EvaluationItemWithMyScore],
)
def upsert_my_evaluation_scores(
    payload: schemas.MyEvaluationUpsertRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.EvaluationItemWithMyScore]:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=400, detail="Employee profile not linked")
    plan = db.get(models.EvaluationPlan, payload.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status != "OPEN":
        raise HTTPException(status_code=400, detail="Plan is not open")

    res = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == payload.plan_id,
            models.EvaluationResult.emp_id == me_emp.id,
            models.EvaluationResult.evaluator_emp_id.is_(None),
        )
        .first()
    )
    if not res:
        res = models.EvaluationResult(
            plan_id=payload.plan_id,
            emp_id=me_emp.id,
            evaluator_emp_id=None,
            score=0,
            comment=None,
        )
        db.add(res)
        db.flush()

    total_weight = 0.0
    weighted_sum = 0.0
    for s in payload.scores:
        item = db.get(models.EvaluationItem, s.item_id)
        if not item or item.plan_id != payload.plan_id:
            continue
        existing = (
            db.query(models.EvaluationScore)
            .filter(
                models.EvaluationScore.result_id == res.id,
                models.EvaluationScore.item_id == s.item_id,
            )
            .first()
        )
        if existing:
            existing.score = s.score
            existing.comment = s.comment
        else:
            db.add(
                models.EvaluationScore(
                    result_id=res.id,
                    item_id=s.item_id,
                    score=s.score,
                    comment=s.comment,
                )
            )
        w = float(item.weight) if item.weight else 1.0
        total_weight += w
        weighted_sum += s.score * w

    res.score = weighted_sum / total_weight if total_weight > 0 else 0
    db.commit()
    db.refresh(res)
    return get_my_evaluation_scores(payload.plan_id, db, current_user)


def _build_item_scores_for_result(
    db: Session,
    plan_id: int,
    result_id: int,
) -> list[schemas.EvaluationItemWithMyScore]:
    items = (
        db.query(models.EvaluationItem)
        .filter(models.EvaluationItem.plan_id == plan_id)
        .order_by(models.EvaluationItem.id)
        .all()
    )
    scores_by_item = {
        sc.item_id: (float(sc.score), sc.comment)
        for sc in db.query(models.EvaluationScore)
        .filter(models.EvaluationScore.result_id == result_id)
        .all()
    }
    return [
        schemas.EvaluationItemWithMyScore(
            id=it.id,
            plan_id=it.plan_id,
            name=it.name,
            weight=float(it.weight),
            category=it.category,
            my_score=scores_by_item.get(it.id, (None, None))[0],
            my_comment=scores_by_item.get(it.id, (None, None))[1],
        )
        for it in items
    ]


@app.post(
    "/api/evaluations/team-scores",
    response_model=list[schemas.EvaluationItemWithMyScore],
)
def upsert_team_evaluation_scores(
    payload: schemas.TeamEvaluationUpsertRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN", "MANAGER")),
) -> list[schemas.EvaluationItemWithMyScore]:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=400, detail="Employee profile not linked")
    plan = db.get(models.EvaluationPlan, payload.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.status != "OPEN":
        raise HTTPException(status_code=400, detail="Plan is not open")

    target_emp = db.get(models.Employee, payload.target_emp_id)
    if not target_emp:
        raise HTTPException(status_code=404, detail="Target employee not found")
    role = getattr(current_user, "role", None)
    if role == "MANAGER" and target_emp.dept_id != me_emp.dept_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    res = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == payload.plan_id,
            models.EvaluationResult.emp_id == payload.target_emp_id,
            models.EvaluationResult.evaluator_emp_id == me_emp.id,
        )
        .first()
    )
    if not res:
        res = models.EvaluationResult(
            plan_id=payload.plan_id,
            emp_id=payload.target_emp_id,
            evaluator_emp_id=me_emp.id,
            score=0,
            comment=None,
        )
        db.add(res)
        db.flush()

    total_weight = 0.0
    weighted_sum = 0.0
    for s in payload.scores:
        item = db.get(models.EvaluationItem, s.item_id)
        if not item or item.plan_id != payload.plan_id:
            continue
        existing = (
            db.query(models.EvaluationScore)
            .filter(
                models.EvaluationScore.result_id == res.id,
                models.EvaluationScore.item_id == s.item_id,
            )
            .first()
        )
        if existing:
            existing.score = s.score
            existing.comment = s.comment
        else:
            db.add(
                models.EvaluationScore(
                    result_id=res.id,
                    item_id=s.item_id,
                    score=s.score,
                    comment=s.comment,
                )
            )
        w = float(item.weight) if item.weight else 1.0
        total_weight += w
        weighted_sum += s.score * w

    res.score = weighted_sum / total_weight if total_weight > 0 else 0
    db.commit()
    db.refresh(res)
    return _build_item_scores_for_result(db, payload.plan_id, res.id)


@app.post("/api/evaluations/plans/{plan_id}/targets/seed")
def seed_evaluation_targets(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> dict[str, int]:
    plan = db.get(models.EvaluationPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    employees = (
        db.query(models.Employee)
        .filter(models.Employee.status == "ACTIVE")
        .all()
    )
    created = 0
    for emp in employees:
        if (
            db.query(models.EvaluationTarget)
            .filter(
                models.EvaluationTarget.plan_id == plan_id,
                models.EvaluationTarget.emp_id == emp.id,
            )
            .first()
        ):
            continue
        target = models.EvaluationTarget(
            plan_id=plan_id,
            emp_id=emp.id,
            status="PENDING",
        )
        db.add(target)
        created += 1
    db.commit()
    return {"created": created}


@app.get(
    "/api/evaluations/plans/{plan_id}/grade-policies",
    response_model=list[schemas.GradePolicyRead],
)
def list_grade_policies(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.GradePolicyRead]:
    if not db.get(models.EvaluationPlan, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    return (
        db.query(models.GradePolicy)
        .filter(models.GradePolicy.plan_id == plan_id)
        .order_by(models.GradePolicy.min_score.desc())
        .all()
    )


@app.post(
    "/api/evaluations/plans/{plan_id}/grade-policies",
    response_model=schemas.GradePolicyRead,
    status_code=201,
)
def create_grade_policy(
    plan_id: int,
    payload: schemas.GradePolicyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.GradePolicyRead:
    if not db.get(models.EvaluationPlan, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    gp = models.GradePolicy(
        plan_id=plan_id,
        min_score=payload.min_score,
        max_score=payload.max_score,
        grade=payload.grade,
        is_promotion_candidate=payload.is_promotion_candidate,
    )
    db.add(gp)
    db.commit()
    db.refresh(gp)
    return gp


@app.post("/api/evaluations/plans/{plan_id}/aggregate")
def aggregate_evaluation_plan(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> dict[str, int]:
    plan = db.get(models.EvaluationPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    policies = (
        db.query(models.GradePolicy)
        .filter(models.GradePolicy.plan_id == plan_id)
        .order_by(models.GradePolicy.min_score)
        .all()
    )
    results = (
        db.query(models.EvaluationResult)
        .filter(models.EvaluationResult.plan_id == plan_id)
        .all()
    )
    updated = 0
    for res in results:
        score = float(res.score)
        grade = None
        is_promo = False
        for gp in policies:
            if gp.min_score <= score <= gp.max_score:
                grade = gp.grade
                is_promo = gp.is_promotion_candidate
                break
        res.grade = grade
        res.is_promotion_candidate = is_promo
        updated += 1
    db.commit()
    return {"updated": updated}


@app.get(
    "/api/evaluations/plans/{plan_id}/promotion-candidates",
    response_model=list[schemas.EmployeeRead],
)
def list_promotion_candidates(
    plan_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> list[schemas.EmployeeRead]:
    if not db.get(models.EvaluationPlan, plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    results = (
        db.query(models.EvaluationResult)
        .filter(
            models.EvaluationResult.plan_id == plan_id,
            models.EvaluationResult.is_promotion_candidate == True,
        )
        .all()
    )
    emp_ids = [r.emp_id for r in results]
    if not emp_ids:
        return []
    employees = db.query(models.Employee).filter(models.Employee.id.in_(emp_ids)).all()
    return list(employees)


# ---- Education / Training ----
@app.get("/api/education/courses", response_model=list[schemas.TrainingCourseRead])
def list_training_courses(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.TrainingCourseRead]:
    return (
        db.query(models.TrainingCourse)
        .order_by(models.TrainingCourse.code)
        .all()
    )


@app.post(
    "/api/education/courses",
    response_model=schemas.TrainingCourseRead,
    status_code=201,
)
def create_training_course(
    payload: schemas.TrainingCourseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.TrainingCourseRead:
    if db.query(models.TrainingCourse).filter(models.TrainingCourse.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Course code already exists")
    course = models.TrainingCourse(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@app.patch(
    "/api/education/courses/{course_id}",
    response_model=schemas.TrainingCourseRead,
)
def update_training_course(
    course_id: int,
    payload: schemas.TrainingCourseUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.TrainingCourseRead:
    course = db.get(models.TrainingCourse, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


@app.get("/api/education/sessions", response_model=list[schemas.TrainingSessionRead])
def list_training_sessions(
    course_id: int | None = Query(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.TrainingSessionRead]:
    q = db.query(models.TrainingSession)
    if course_id is not None:
        q = q.filter(models.TrainingSession.course_id == course_id)
    return q.order_by(models.TrainingSession.start_date, models.TrainingSession.id).all()


@app.post(
    "/api/education/sessions",
    response_model=schemas.TrainingSessionRead,
    status_code=201,
)
def create_training_session(
    payload: schemas.TrainingSessionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.TrainingSessionRead:
    if not db.get(models.TrainingCourse, payload.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    session = models.TrainingSession(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.patch(
    "/api/education/sessions/{session_id}",
    response_model=schemas.TrainingSessionRead,
)
def update_training_session(
    session_id: int,
    payload: schemas.TrainingSessionUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.TrainingSessionRead:
    session = db.get(models.TrainingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(session, k, v)
    db.commit()
    db.refresh(session)
    return session


@app.get(
    "/api/education/my-enrollments",
    response_model=list[schemas.TrainingEnrollmentRead],
)
def list_my_enrollments(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.TrainingEnrollmentRead]:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []
    return (
        db.query(models.TrainingEnrollment)
        .filter(models.TrainingEnrollment.emp_id == me_emp.id)
        .order_by(models.TrainingEnrollment.created_at.desc())
        .all()
    )


@app.post(
    "/api/education/enroll",
    response_model=schemas.TrainingEnrollmentRead,
    status_code=201,
)
def enroll_training(
    payload: schemas.TrainingEnrollmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.TrainingEnrollmentRead:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=400, detail="Employee profile not linked")
    session = db.get(models.TrainingSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    existing = (
        db.query(models.TrainingEnrollment)
        .filter(
            models.TrainingEnrollment.session_id == payload.session_id,
            models.TrainingEnrollment.emp_id == me_emp.id,
        )
        .first()
    )
    if existing:
        return existing

    enr = models.TrainingEnrollment(
        session_id=payload.session_id,
        emp_id=me_emp.id,
        status="REQUESTED",
    )
    db.add(enr)
    db.commit()
    db.refresh(enr)
    return enr


@app.patch(
    "/api/education/enrollments/{enrollment_id}",
    response_model=schemas.TrainingEnrollmentRead,
)
def update_training_enrollment(
    enrollment_id: int,
    payload: schemas.EnrollmentStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.TrainingEnrollmentRead:
    enr = db.get(models.TrainingEnrollment, enrollment_id)
    if not enr:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    if payload.status not in ("APPROVED", "COMPLETED", "CANCELLED"):
        raise HTTPException(status_code=400, detail="Invalid status")
    enr.status = payload.status
    db.commit()
    db.refresh(enr)
    return enr


# ---- Benefits ----
@app.get("/api/benefits/policies", response_model=list[schemas.BenefitPolicyRead])
def list_benefit_policies(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.BenefitPolicyRead]:
    return (
        db.query(models.BenefitPolicy)
        .filter(models.BenefitPolicy.is_active == True)
        .order_by(models.BenefitPolicy.code)
        .all()
    )


@app.post(
    "/api/benefits/policies",
    response_model=schemas.BenefitPolicyRead,
    status_code=201,
)
def create_benefit_policy(
    payload: schemas.BenefitPolicyCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.BenefitPolicyRead:
    if db.query(models.BenefitPolicy).filter(models.BenefitPolicy.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Policy code already exists")
    bp = models.BenefitPolicy(**payload.model_dump())
    db.add(bp)
    db.commit()
    db.refresh(bp)
    return bp


@app.post(
    "/api/benefits/balances",
    response_model=schemas.PointBalanceRead,
    status_code=201,
)
def create_point_balance(
    payload: schemas.PointBalanceCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.PointBalanceRead:
    if not db.get(models.Employee, payload.emp_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    if not db.get(models.BenefitPolicy, payload.policy_id):
        raise HTTPException(status_code=404, detail="Policy not found")
    existing = (
        db.query(models.PointBalance)
        .filter(
            models.PointBalance.emp_id == payload.emp_id,
            models.PointBalance.policy_id == payload.policy_id,
            models.PointBalance.year == payload.year,
        )
        .first()
    )
    if existing:
        return existing
    bal = models.PointBalance(
        emp_id=payload.emp_id,
        policy_id=payload.policy_id,
        year=payload.year,
        balance=payload.initial_balance,
    )
    db.add(bal)
    db.commit()
    db.refresh(bal)
    return bal


@app.get(
    "/api/benefits/my-balances",
    response_model=list[schemas.PointBalanceRead],
)
def list_my_point_balances(
    year: int | None = Query(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.PointBalanceRead]:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        return []
    q = db.query(models.PointBalance).filter(models.PointBalance.emp_id == me_emp.id)
    if year is not None:
        q = q.filter(models.PointBalance.year == year)
    return q.all()


@app.post(
    "/api/benefits/transactions",
    response_model=schemas.PointTransactionRead,
    status_code=201,
)
def create_point_transaction(
    payload: schemas.PointTransactionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> schemas.PointTransactionRead:
    bal = db.get(models.PointBalance, payload.balance_id)
    if not bal:
        raise HTTPException(status_code=404, detail="Balance not found")
    amt = payload.amount
    if payload.txn_type in ("USE", "EXPIRE"):
        amt = -abs(amt)
    elif payload.txn_type in ("GRANT", "ADJUST"):
        amt = abs(amt)
    else:
        raise HTTPException(status_code=400, detail="Invalid txn_type")
    bal.balance = float(bal.balance) + amt
    if float(bal.balance) < 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    txn = models.PointTransaction(
        balance_id=payload.balance_id,
        amount=amt,
        txn_type=payload.txn_type,
        memo=payload.memo,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ---- Common Codes ----
@app.get("/api/codes/groups", response_model=list[schemas.CodeGroupRead])
def list_code_groups(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.CodeGroupRead]:
    return db.query(models.CodeGroup).order_by(models.CodeGroup.code).all()


@app.get("/api/codes/groups/{group_code}/codes", response_model=list[schemas.CodeRead])
def list_codes_by_group(
    group_code: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.CodeRead]:
    grp = db.query(models.CodeGroup).filter(models.CodeGroup.code == group_code).first()
    if not grp:
        raise HTTPException(status_code=404, detail="Code group not found")
    return (
        db.query(models.Code)
        .filter(models.Code.group_id == grp.id, models.Code.is_active == True)
        .order_by(models.Code.sort_order, models.Code.code)
        .all()
    )


# ---- Audit Log ----
@app.get("/api/audit-logs", response_model=list[schemas.AuditLogRead])
def list_audit_logs(
    entity_type: str | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_roles("ADMIN", "HR_ADMIN")),
) -> list[schemas.AuditLogRead]:
    q = db.query(models.AuditLog)
    if entity_type:
        q = q.filter(models.AuditLog.entity_type == entity_type)
    return q.order_by(models.AuditLog.created_at.desc()).limit(limit).all()


# ---- Time Log (출퇴근) ----
@app.get("/api/attendance/time-logs", response_model=list[schemas.TimeLogRead])
def list_time_logs(
    emp_id: int | None = Query(None),
    year_month: str | None = Query(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> list[schemas.TimeLogRead]:
    role = getattr(current_user, "role", None)
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp and role not in ("ADMIN", "HR_ADMIN"):
        return []
    q = db.query(models.TimeLog)
    if emp_id is not None:
        if role in ("ADMIN", "HR_ADMIN"):
            pass
        elif role == "MANAGER":
            target = db.get(models.Employee, emp_id)
            if not me_emp or not target or target.dept_id != me_emp.dept_id:
                return []
        else:
            if not me_emp or emp_id != me_emp.id:
                return []
        q = q.filter(models.TimeLog.emp_id == emp_id)
    else:
        if role not in ("ADMIN", "HR_ADMIN"):
            q = q.filter(models.TimeLog.emp_id == me_emp.id)
    if year_month:
        from datetime import datetime as dt
        y, m = int(year_month[:4]), int(year_month[4:6])
        start = dt(y, m, 1)
        end = dt(y, m + 1, 1) if m < 12 else dt(y + 1, 1, 1)
        q = q.filter(
            models.TimeLog.log_datetime >= start,
            models.TimeLog.log_datetime < end,
        )
    return q.order_by(models.TimeLog.log_datetime.desc()).limit(500).all()


@app.post(
    "/api/attendance/time-logs",
    response_model=schemas.TimeLogRead,
    status_code=201,
)
def create_time_log(
    payload: schemas.TimeLogCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
) -> schemas.TimeLogRead:
    me_emp = (
        db.query(models.Employee)
        .filter(models.Employee.user_id == current_user.id)
        .first()
    )
    if not me_emp:
        raise HTTPException(status_code=400, detail="Employee profile not linked")
    emp_id = payload.emp_id if payload.emp_id is not None else me_emp.id
    if emp_id != me_emp.id:
        role = getattr(current_user, "role", None)
        if role not in ("ADMIN", "HR_ADMIN"):
            raise HTTPException(status_code=403, detail="Not enough permissions")
    tl = models.TimeLog(
        emp_id=emp_id,
        log_datetime=payload.log_datetime,
        log_type=payload.log_type,
        source=payload.source,
    )
    db.add(tl)
    db.commit()
    db.refresh(tl)
    return tl

