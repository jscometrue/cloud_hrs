## Ⅰ. 개요

- **목적**: 인사시스템(HR System)의 메뉴 구조, 기본 업무 로직, 데이터 흐름 및 DB 테이블 구조를 일관되게 정리한 **설계·운영 매뉴얼**입니다.
- **대상 독자**: 인사시스템 기획자, 개발자, 운영자(시스템관리자).

---

## Ⅱ. 시스템 전체 구조

### 1. 상위 메뉴 구조 (L1 기준)

1. **조직·인사기본**
2. **근태관리**
3. **급여·보상관리**
4. **평가·승진관리**
5. **교육·역량관리**
6. **복리후생관리**
7. **보고서·대시보드**
8. **시스템관리**

각 상위 메뉴는 최대 **레벨 5까지 세분화**할 수 있도록 설계합니다.

---

## Ⅲ. 메뉴 구성 상세

### 1. 조직·인사기본

- **1. 조직·인사기본**
  - 1-1. 조직관리
    - 1-1-1. 조직도 조회  
      - 1-1-1-1. 조직도 트리 보기  
        - 1-1-1-1-1. 조직도 Export(엑셀/이미지)
      - 1-1-1-2. 조직 변경 이력 보기  
        - 1-1-1-2-1. 특정일 기준 조직 스냅샷
    - 1-1-2. 조직정보 관리  
      - 1-1-2-1. 조직 단위 등록/수정  
        - 1-1-2-1-1. 기본정보(코드, 명칭, 상위조직)  
        - 1-1-2-1-2. 예산·정원 정보  
      - 1-1-2-2. 조직 폐지/통합 관리  
        - 1-1-2-2-1. 조직 폐지 이력
  - 1-2. 인사기본정보  
    - 1-2-1. 사원조회(재직/퇴직, 상세 프로필, 퇴사이력 등)
    - 1-2-2. 사원등록/변경(신규입사, 인사이동, 퇴직처리 등)
  - 1-3. 인사 Master 관리  
    - 코드관리(직급/직군, 근무형태 등), 직무·직책 관리

### 2. 근태관리

- **2. 근태관리**
  - 2-1. 근태기본설정(근무체계, 근무일정, 휴가정책)
  - 2-2. 근태입력·승인(출퇴근 기록, 휴가신청·승인)
  - 2-3. 근태마감(월간 근태집계, 급여연동 파일 생성)

### 3. 급여·보상관리

- **3. 급여·보상관리**
  - 3-1. 급여기본설정(급여항목, 세율·보험요율)
  - 3-2. 급여계산(대상자 확정, 근태반영, 시뮬레이션)
  - 3-3. 급여지급·정산(명세서, 은행이체, 연말정산)

### 4. 평가·승진관리

- **4. 평가·승진관리**
  - 4-1. 평가기준 설정(평가항목, 가중치)
  - 4-2. 평가실행(대상자 설정, 자기평가, 상사·다면평가)
  - 4-3. 평가결과·승진연계(등급 산정, 승진대상자 추천, 이의신청 관리)

### 5. 교육·역량관리

- **5. 교육·역량관리**
  - 5-1. 교육과정 관리(과정 개설, 대상자 선정, 자동 추천)
  - 5-2. 수강·이수 관리(교육신청, 이수처리)

### 6. 복리후생관리 (요약)

- 복지포인트, 선택형 복리후생, 식대, 기숙사 등 복지 제도 운영.

### 7. 보고서·대시보드 (요약)

- 인력현황, 이직률, 인건비, 근태·초과근로, 평가분포 등 HR KPI 대시보드.

### 8. 시스템관리 (상세)

- **8. 시스템관리**
  - 8-1. 사용자·조직권한 관리  
    - 사용자 관리(계정 생성/잠금), 조직·직무 기반 권한
  - 8-2. 메뉴·역할권한 관리  
    - 메뉴 구조, 역할(Role), 역할별 메뉴권한
  - 8-3. 보안·인증 설정  
    - 비밀번호 정책, 접속제어(IP, 세션), SSO/2FA
  - 8-4. 공통코드·환경설정  
    - 공통코드, 시스템 환경변수, 다국어 레이블
  - 8-5. 인터페이스·연계관리  
    - ERP/그룹웨어/근태장비 연계, 송수신 로그
  - 8-6. 로그·감사추적  
    - 접속로그, 데이터 변경이력, 감사 리포트
  - 8-7. 배치·스케줄 관리  
    - 근태마감, 급여, 알림 등 배치 설정·모니터링
  - 8-8. 알림·메시지 관리  
    - 템플릿, 이벤트·채널 매핑, 발송이력
  - 8-9. 시스템 운영도구  
    - 백업·복구, 성능 모니터링, 버전·배포 이력

---

## Ⅳ. 기본 로직 및 업무 흐름

### 1. 인사·조직 관리 로직

- **사원 Master 생성·유지**
  - 신규입사 → `사원등록`에서 인적·조직·직급·급여정보 입력 → `사원 Master` 생성.
  - 인사이동(부서/직급/직책) → 이력 테이블 기록, 기준일자 조회 지원.
  - 퇴직처리 → 상태(재직/퇴직) 변경 + 퇴직이력 기록 → 급여·근태 대상에서 제외.

- **조직 관리**
  - 조직은 상위/하위 트리 구조로 관리, 유효시작·종료일로 이력 관리.
  - 특정 일자를 기준으로 당시 조직 구조 복원(조직도 스냅샷).

### 2. 근태 → 급여 연계 로직

1. 출퇴근 기록(단말기/모바일/웹) + 휴가/출장/재택 신청·승인 수집.
2. 월 단위 `근태집계`에서 근로시간, 연장·야간·휴일, 휴가, 이상근태(지각·조퇴·결근) 산출.
3. `급여계산`에서 근태 집계 데이터를 불러와 수당(연장·야간·휴일) 및 공제(결근 등)에 반영.

### 3. 급여계산 로직

1. **기본정보**: 사원별 기본급, 수당, 공제, 세율·보험요율.
2. **계산 흐름**
   - 급여대상자 확정 → 근태·인사변동 반영 → 항목별 계산식 적용 → 세금·보험 공제 → 실지급액 산출.
3. **결과 활용**
   - 급여명세서 생성, 은행이체 파일 생성, ERP 회계전표 연계.

### 4. 평가·승진 로직

1. 평가계획·기준(항목, 가중치, 평가자 구조) 설정.
2. 자기평가, 상사평가, 다면평가 입력.
3. 평가결과 집계 후 최종 점수·등급 산출.
4. 승진·보상 기준에 따라 자동 승진/성과급 후보 생성 → 인사발령·보상 모듈로 연계.

### 5. 교육·역량 로직

- 직무·직급별 역량모델 정의 → 평가결과/진단으로 역량 수준 파악 → 부족 역량에 매핑된 교육과정 자동 추천 → 교육 이수 후 역량 점수 갱신.

### 6. 시스템관리 로직 (요약)

- **권한 모델**: 사용자·조직·직무 → 역할(Role) → 역할별 메뉴권한 → 실행 시점에 최종 권한 계산.
- **보안·감사**: 로그인/중요데이터 변경 시 로그와 감사 이력 기록.
- **배치·인터페이스**: 정기작업(근태마감, 급여, 알림) 및 외부 시스템 연계 자동 실행·모니터링.
- **환경설정**: 공통코드, 환경변수, 알림 템플릿이 전 모듈의 공통 기준 데이터.

---

## Ⅴ. 데이터 흐름(개념)

### 1. 주요 흐름 개요

- 채용/입사 → **사원 Master**
- 사원 Master + 조직정보 → 근태, 급여, 평가, 교육, 복리후생의 기준데이터
- 근태집계 → 급여계산
- 평가결과 → 승진/보상 및 역량진단
- 급여/근태/평가/교육 데이터 → 보고서·대시보드

### 2. 개념 흐름도 (텍스트 설명)

- **사원 Master**와 **조직정보**는 모든 모듈의 공통 기준.
- **근태** 결과는 **급여**에 직접 연동.
- **평가** 결과는 **승진·보상**과 **역량/교육**에 연계되고, 교육 이수 결과는 다시 역량에 반영.
- 모든 주요 데이터는 **보고서·대시보드**에서 집계·시각화.

---

## Ⅵ. DB 테이블 구조 개요

### 1. 공통·기준

- **회사/조직/직무/직급**
  - `CM_COMPANY`, `CM_DEPT`, `CM_DEPT_HIST`, `CM_JOB`, `CM_POS`
- **공통코드**
  - `CM_CODE_GROUP`, `CM_CODE`

### 2. 조직·인사

- **사원 Master 및 이력**
  - `HR_EMP` : 사원 기본정보
  - `HR_EMP_JOB_HIST` : 인사이동 이력(부서·직무·직급)
  - `HR_EMP_PAY_BASE` : 급여기본정보
  - `HR_EMP_STATUS_HIST` : 재직/휴직/퇴직 상태이력

### 3. 근태

- **근무기준·스케줄**
  - `AT_WORK_CALENDAR`, `AT_WORK_TYPE`, `AT_WORK_SCHEDULE`
- **실적·신청·집계**
  - `AT_TIMELOG` : 출퇴근 기록
  - `AT_LEAVE_REQ` : 휴가/근태 신청
  - `AT_LEAVE_BALANCE` : 휴가잔여
  - `AT_MONTH_SUMMARY` : 월 근태집계(급여 연동 기준)

### 4. 급여·보상

- **기본 설정**
  - `PY_PAY_GROUP`, `PY_ITEM`, `PY_ITEM_MAP`
- **급여 실행/결과**
  - `PY_RUN` : 급여차수(년월·타입)
  - `PY_RESULT` : 개인별 급여 헤더(총지급·총공제·실지급)
  - `PY_RESULT_ITEM` : 급여항목별 상세
  - `PY_BANK_FILE` : 은행이체 파일
  - `PY_YEAR_SETTLE` : 연말정산 결과(요약)

### 5. 평가·승진

- **평가 계획·항목**
  - `EV_PLAN`, `EV_ITEM`
- **평가 대상·평가자**
  - `EV_TARGET`, `EV_EVALUATOR`
- **결과·요약**
  - `EV_RESULT` : 항목별 점수·코멘트
  - `EV_SUMMARY` : 최종 점수·등급
  - `EV_PROMOTION_CANDIDATE` : 승진대상자 후보

### 6. 교육·역량

- **역량모델·항목**
  - `TR_COMPETENCY_MODEL`, `TR_COMPETENCY_ITEM`
- **교육과정·회차**
  - `TR_COURSE`, `TR_COURSE_COMP_MAP`, `TR_SESSION`
- **수강·진단**
  - `TR_ENROLL` : 교육신청·이수
  - `TR_COMP_EVAL` : 역량진단 결과

### 7. 복리후생 (요약)

- `WF_BENEFIT_POLICY`, `WF_POINT_BALANCE`, `WF_POINT_TXN`

### 8. 시스템관리

- **사용자·역할·메뉴**
  - `SM_USER`, `SM_ROLE`, `SM_USER_ROLE`, `SM_MENU`, `SM_ROLE_MENU_AUTH`
- **보안·로그·감사**
  - `SM_LOGIN_LOG`, `SM_AUDIT_LOG`, `SM_SECURITY_POLICY`
- **인터페이스·배치·알림**
  - `SM_IF_SCENARIO`, `SM_IF_CONFIG`, `SM_IF_LOG`
  - `SM_BATCH_JOB`, `SM_BATCH_SCHEDULE`, `SM_BATCH_LOG`
  - `SM_MSG_TEMPLATE`, `SM_MSG_EVENT_RULE`, `SM_MSG_LOG`
- **환경·백업**
  - `SM_CONFIG`, `SM_BACKUP_LOG`

---

## Ⅶ. 구축·확장 가이드

- **메뉴 → 기능 → 테이블 매핑**을 기준으로, 화면/API 설계 시 각 기능이 어떤 테이블을 조회/저장하는지 명시합니다.
- 회사별 요구사항에 따라:
  - 메뉴 깊이(L3~L5)와 세부 기능은 **필요 기능만 남기고 슬림화**할 수 있습니다.
  - DB 컬럼은 실제 규정(예: 급여체계, 평가척도, 복지정책)에 맞춰 확장합니다.
- 추후 단계:
  - **ERD(테이블 관계도)**, **시퀀스 다이어그램(주요 업무 시나리오)**, **화면 설계서**를 이 매뉴얼을 기준으로 세분화하면 됩니다.

---

## Ⅷ. 주요 테이블별 컬럼 정의서 (근태 + 급여 중심)

아래 컬럼 정의서는 설계 및 개발 기준이며, 실제 DBMS 별 타입은 프로젝트 환경에 맞게 조정합니다.  
데이터 타입 예시는 다음과 같습니다.

- **PK**: Primary Key, **FK**: Foreign Key
- 타입 예시: `INT`, `BIGINT`, `VARCHAR(n)`, `DATE`, `DATETIME`, `DECIMAL(15,2)`, `BOOLEAN`

### 1. 공통/인사 영역

#### 1.1 `HR_EMP` (Employee Master)

| Column Name     | Type            | Key | Description                          |
|-----------------|-----------------|-----|--------------------------------------|
| `id`            | BIGINT          | PK  | Employee unique ID                   |
| `emp_no`        | VARCHAR(20)     |     | Employee number (HR code)           |
| `first_name`    | VARCHAR(50)     |     | First name                           |
| `last_name`     | VARCHAR(50)     |     | Last name                            |
| `email`         | VARCHAR(100)    |     | Company email                        |
| `phone`         | VARCHAR(30)     |     | Mobile phone                         |
| `hire_date`     | DATE            |     | Hire date                            |
| `terminate_date`| DATE            |     | Termination date (nullable)          |
| `status`        | VARCHAR(20)     |     | Employment status (ACTIVE/INACTIVE) |
| `dept_id`       | BIGINT          | FK  | Current department (`CM_DEPT.id`)    |
| `pay_group_id`  | BIGINT          | FK  | Pay group (`PY_PAY_GROUP.id`)        |
| `created_at`    | DATETIME        |     | Record created datetime              |
| `updated_at`    | DATETIME        |     | Last updated datetime                |

#### 1.2 `CM_DEPT` (Department)

| Column Name      | Type         | Key | Description                          |
|------------------|--------------|-----|--------------------------------------|
| `id`             | BIGINT       | PK  | Department unique ID                 |
| `code`           | VARCHAR(20)  |     | Department code                      |
| `name`           | VARCHAR(100) |     | Department name                      |
| `parent_id`      | BIGINT       | FK  | Parent department (`CM_DEPT.id`)     |
| `effective_from` | DATE         |     | Valid from date                      |
| `effective_to`   | DATE         |     | Valid to date (nullable)             |
| `headcount_limit`| INT          |     | Headcount limit (nullable)           |
| `created_at`     | DATETIME     |     | Created datetime                     |
| `updated_at`     | DATETIME     |     | Updated datetime                     |

---

### 2. 근태(Attendance) 영역

#### 2.1 `AT_WORK_CALENDAR` (Work Calendar)

| Column Name   | Type       | Key | Description                              |
|---------------|------------|-----|------------------------------------------|
| `id`          | BIGINT     | PK  | Calendar record ID                       |
| `work_date`   | DATE       |     | Calendar date                            |
| `is_workday`  | BOOLEAN    |     | Is normal workday                        |
| `is_holiday`  | BOOLEAN    |     | Is public holiday                        |
| `holiday_code`| VARCHAR(20)|     | Holiday code (nullable)                  |
| `created_at`  | DATETIME   |     | Created datetime                         |
| `updated_at`  | DATETIME   |     | Updated datetime                         |

#### 2.2 `AT_WORK_TYPE` (Work Type / Shift Pattern)

| Column Name    | Type         | Key | Description                              |
|----------------|--------------|-----|------------------------------------------|
| `id`           | BIGINT       | PK  | Work type ID                             |
| `code`         | VARCHAR(20)  |     | Work type code                           |
| `name`         | VARCHAR(100) |     | Work type name (e.g. DAY_SHIFT)         |
| `start_time`   | VARCHAR(5)   |     | Planned start time (HH:MM)              |
| `end_time`     | VARCHAR(5)   |     | Planned end time (HH:MM)                |
| `break_minutes`| INT          |     | Break minutes                            |
| `created_at`   | DATETIME     |     | Created datetime                         |
| `updated_at`   | DATETIME     |     | Updated datetime                         |

#### 2.3 `AT_WORK_SCHEDULE` (Employee Work Schedule)

| Column Name   | Type     | Key | Description                               |
|---------------|----------|-----|-------------------------------------------|
| `id`          | BIGINT   | PK  | Schedule ID                               |
| `emp_id`      | BIGINT   | FK  | Employee (`HR_EMP.id`)                    |
| `work_date`   | DATE     |     | Work date                                 |
| `work_type_id`| BIGINT   | FK  | Work type (`AT_WORK_TYPE.id`)             |
| `planned_start`| DATETIME|     | Planned start datetime                    |
| `planned_end` | DATETIME |     | Planned end datetime                      |
| `created_at`  | DATETIME |     | Created datetime                          |
| `updated_at`  | DATETIME |     | Updated datetime                          |

#### 2.4 `AT_TIMELOG` (Time Log)

| Column Name   | Type       | Key | Description                               |
|---------------|------------|-----|-------------------------------------------|
| `id`          | BIGINT     | PK  | Time log ID                               |
| `emp_id`      | BIGINT     | FK  | Employee (`HR_EMP.id`)                    |
| `log_datetime`| DATETIME   |     | Log datetime                              |
| `log_type`    | VARCHAR(10)|     | IN / OUT                                  |
| `source`      | VARCHAR(20)|     | Source (DEVICE / WEB / MOBILE)           |
| `device_id`   | VARCHAR(50)|     | Device identifier (nullable)             |
| `created_at`  | DATETIME   |     | Created datetime                          |

#### 2.5 `AT_LEAVE_REQ` (Leave Request)

| Column Name    | Type         | Key | Description                              |
|----------------|--------------|-----|------------------------------------------|
| `id`           | BIGINT       | PK  | Leave request ID                         |
| `emp_id`       | BIGINT       | FK  | Employee (`HR_EMP.id`)                   |
| `leave_type`   | VARCHAR(20)  |     | Leave type code (ANNUAL, SICK, etc.)     |
| `start_datetime`| DATETIME    |     | Leave start datetime                     |
| `end_datetime` | DATETIME     |     | Leave end datetime                       |
| `hours`        | DECIMAL(5,2) |     | Total leave hours                        |
| `status`       | VARCHAR(20)  |     | REQUESTED / APPROVED / REJECTED          |
| `reason`       | VARCHAR(255) |     | Reason (nullable)                        |
| `created_at`   | DATETIME     |     | Created datetime                         |
| `updated_at`   | DATETIME     |     | Updated datetime                         |

#### 2.6 `AT_LEAVE_BALANCE` (Leave Balance)

| Column Name | Type          | Key | Description                              |
|-------------|---------------|-----|------------------------------------------|
| `id`        | BIGINT        | PK  | Leave balance ID                         |
| `emp_id`    | BIGINT        | FK  | Employee (`HR_EMP.id`)                   |
| `year`      | INT           |     | Year                                     |
| `entitled_days`| DECIMAL(5,2)|    | Entitled days                            |
| `used_days` | DECIMAL(5,2)  |     | Used days                                |
| `remaining_days`| DECIMAL(5,2)|   | Remaining days                           |
| `created_at`| DATETIME      |     | Created datetime                         |
| `updated_at`| DATETIME      |     | Updated datetime                         |

#### 2.7 `AT_MONTH_SUMMARY` (Monthly Attendance Summary)

| Column Name       | Type           | Key | Description                              |
|-------------------|----------------|-----|------------------------------------------|
| `id`              | BIGINT         | PK  | Summary ID                               |
| `emp_id`          | BIGINT         | FK  | Employee (`HR_EMP.id`)                   |
| `year_month`      | VARCHAR(6)     |     | Year-month (YYYYMM)                      |
| `planned_hours`   | DECIMAL(7,2)   |     | Planned working hours                    |
| `worked_hours`    | DECIMAL(7,2)   |     | Actual worked hours                      |
| `overtime_hours`  | DECIMAL(7,2)   |     | Overtime hours                           |
| `night_hours`     | DECIMAL(7,2)   |     | Night work hours                         |
| `holiday_hours`   | DECIMAL(7,2)   |     | Holiday work hours                       |
| `late_count`      | INT            |     | Count of late                            |
| `early_leave_count`| INT           |     | Count of early leave                     |
| `absence_count`   | INT            |     | Count of absence                         |
| `is_locked`       | BOOLEAN        |     | Locked for payroll (Y/N)                 |
| `created_at`      | DATETIME       |     | Created datetime                         |
| `updated_at`      | DATETIME       |     | Updated datetime                         |

---

### 3. 급여(Payroll) 영역

#### 3.1 `PY_PAY_GROUP` (Pay Group)

| Column Name   | Type         | Key | Description                              |
|---------------|--------------|-----|------------------------------------------|
| `id`          | BIGINT       | PK  | Pay group ID                             |
| `code`        | VARCHAR(20)  |     | Pay group code                           |
| `name`        | VARCHAR(100) |     | Pay group name                           |
| `pay_cycle`   | VARCHAR(20)  |     | MONTHLY / WEEKLY / BIWEEKLY             |
| `cutoff_day`  | INT          |     | Cutoff day of month                      |
| `pay_day`     | INT          |     | Payment day of month                     |
| `created_at`  | DATETIME     |     | Created datetime                         |
| `updated_at`  | DATETIME     |     | Updated datetime                         |

#### 3.2 `PY_ITEM` (Payroll Item)

| Column Name    | Type          | Key | Description                              |
|----------------|---------------|-----|------------------------------------------|
| `id`           | BIGINT        | PK  | Payroll item ID                          |
| `code`         | VARCHAR(20)   |     | Payroll item code                        |
| `name`         | VARCHAR(100)  |     | Payroll item name                        |
| `item_type`    | VARCHAR(20)   |     | EARNING / DEDUCTION                      |
| `taxable`      | BOOLEAN       |     | Is taxable                               |
| `calculation_type`| VARCHAR(20)|     | FIXED / RATE / FORMULA                   |
| `default_amount` | DECIMAL(15,2)|    | Default amount (nullable)                |
| `created_at`   | DATETIME      |     | Created datetime                         |
| `updated_at`   | DATETIME      |     | Updated datetime                         |

#### 3.3 `PY_RUN` (Payroll Run)

| Column Name   | Type         | Key | Description                              |
|---------------|--------------|-----|------------------------------------------|
| `id`          | BIGINT       | PK  | Payroll run ID                           |
| `pay_group_id`| BIGINT       | FK  | Pay group (`PY_PAY_GROUP.id`)           |
| `year_month`  | VARCHAR(6)   |     | Year-month (YYYYMM)                      |
| `run_type`    | VARCHAR(20)  |     | REGULAR / BONUS / SEVERANCE             |
| `status`      | VARCHAR(20)  |     | DRAFT / CALCULATED / CONFIRMED          |
| `calculated_at`| DATETIME    |     | Calculated datetime (nullable)           |
| `paid_at`     | DATETIME     |     | Paid datetime (nullable)                 |
| `created_at`  | DATETIME     |     | Created datetime                         |
| `updated_at`  | DATETIME     |     | Updated datetime                         |

#### 3.4 `PY_RESULT` (Payroll Result Header)

| Column Name    | Type          | Key | Description                              |
|----------------|---------------|-----|------------------------------------------|
| `id`           | BIGINT        | PK  | Payroll result ID                        |
| `pay_run_id`   | BIGINT        | FK  | Payroll run (`PY_RUN.id`)                |
| `emp_id`       | BIGINT        | FK  | Employee (`HR_EMP.id`)                   |
| `gross_amount` | DECIMAL(15,2) |     | Total earnings                           |
| `deduct_amount`| DECIMAL(15,2) |     | Total deductions                         |
| `net_amount`   | DECIMAL(15,2) |     | Net payment                              |
| `currency`     | VARCHAR(10)   |     | Currency code (e.g. KRW)                 |
| `status`       | VARCHAR(20)   |     | CALCULATED / CONFIRMED                   |
| `created_at`   | DATETIME      |     | Created datetime                         |
| `updated_at`   | DATETIME      |     | Updated datetime                         |

#### 3.5 `PY_RESULT_ITEM` (Payroll Result Detail)

| Column Name    | Type          | Key | Description                              |
|----------------|---------------|-----|------------------------------------------|
| `id`           | BIGINT        | PK  | Payroll result item ID                   |
| `pay_result_id`| BIGINT        | FK  | Payroll result (`PY_RESULT.id`)          |
| `pay_item_id`  | BIGINT        | FK  | Payroll item (`PY_ITEM.id`)              |
| `amount`       | DECIMAL(15,2) |     | Calculated amount                        |
| `quantity`     | DECIMAL(10,2) |     | Quantity (hours, days, etc.)             |
| `rate`         | DECIMAL(10,4) |     | Rate (nullable)                          |
| `memo`         | VARCHAR(255)  |     | Additional note (nullable)               |
| `created_at`   | DATETIME      |     | Created datetime                         |
| `updated_at`   | DATETIME      |     | Updated datetime                         |

---

### 4. 시스템관리(일부) 영역

#### 4.1 `SM_USER` (System User)

| Column Name     | Type         | Key | Description                              |
|-----------------|--------------|-----|------------------------------------------|
| `id`            | BIGINT       | PK  | User ID                                  |
| `username`      | VARCHAR(50)  |     | Login ID                                 |
| `password_hash` | VARCHAR(255) |     | Password hash                            |
| `email`         | VARCHAR(100) |     | User email                               |
| `is_active`     | BOOLEAN      |     | Active flag                              |
| `last_login_at` | DATETIME     |     | Last login datetime (nullable)           |
| `created_at`    | DATETIME     |     | Created datetime                         |
| `updated_at`    | DATETIME     |     | Updated datetime                         |

#### 4.2 `SM_ROLE` (Role)

| Column Name | Type         | Key | Description                              |
|-------------|--------------|-----|------------------------------------------|
| `id`        | BIGINT       | PK  | Role ID                                  |
| `code`      | VARCHAR(50)  |     | Role code                                |
| `name`      | VARCHAR(100) |     | Role name                                |
| `created_at`| DATETIME     |     | Created datetime                         |
| `updated_at`| DATETIME     |     | Updated datetime                         |

#### 4.3 `SM_USER_ROLE` (User-Role Mapping)

| Column Name | Type   | Key | Description                              |
|-------------|--------|-----|------------------------------------------|
| `id`        | BIGINT | PK  | User-role mapping ID                     |
| `user_id`   | BIGINT | FK  | User (`SM_USER.id`)                      |
| `role_id`   | BIGINT | FK  | Role (`SM_ROLE.id`)                      |

#### 4.4 `SM_MENU` (Menu)

| Column Name | Type         | Key | Description                              |
|-------------|--------------|-----|------------------------------------------|
| `id`        | BIGINT       | PK  | Menu ID                                  |
| `parent_id` | BIGINT       | FK  | Parent menu (`SM_MENU.id`)              |
| `code`      | VARCHAR(50)  |     | Menu code                                |
| `name`      | VARCHAR(100) |     | Menu name                                |
| `path`      | VARCHAR(200) |     | Route path or URL                        |
| `icon`      | VARCHAR(50)  |     | Icon name (nullable)                     |
| `sort_order`| INT          |     | Display order                            |
| `created_at`| DATETIME     |     | Created datetime                         |
| `updated_at`| DATETIME     |     | Updated datetime                         |

#### 4.5 `SM_ROLE_MENU_AUTH` (Role-Menu Authorization)

| Column Name | Type    | Key | Description                              |
|-------------|---------|-----|------------------------------------------|
| `id`        | BIGINT  | PK  | Role-menu auth ID                        |
| `role_id`   | BIGINT  | FK  | Role (`SM_ROLE.id`)                      |
| `menu_id`   | BIGINT  | FK  | Menu (`SM_MENU.id`)                      |
| `can_view`  | BOOLEAN |     | Can view                                 |
| `can_create`| BOOLEAN |     | Can create                               |
| `can_update`| BOOLEAN |     | Can update                               |
| `can_delete`| BOOLEAN |     | Can delete                               |

