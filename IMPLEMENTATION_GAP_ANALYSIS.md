# HR 시스템 구현 현황 vs HR_System_Manual.md 비교

## 1. 메뉴·기능별 구현 현황

| L1 메뉴 | L2/L3 기능 | 매뉴얼 상세 | 구현 상태 | 미구현 내용 |
|---------|------------|-------------|-----------|-------------|
| **1. 조직·인사기본** | 1-1 조직관리 | 조직도 조회, 트리 보기, Export | ❌ 미구현 | 조직도 트리 UI, Export(엑셀/이미지) |
| | | 조직 변경 이력, 특정일 스냅샷 | ❌ 미구현 | 조직 이력 테이블(CM_DEPT_HIST), 스냅샷 조회 |
| | | 조직정보 관리(단위 등록/수정) | ✅ 구현 | departments CRUD |
| | | 예산·정원 정보 | ❌ 미구현 | headcount_limit만 있음, 예산 정보 없음 |
| | | 조직 폐지/통합 관리 | ❌ 미구현 | 폐지·통합 이력, 관리 화면 |
| | 1-2 인사기본정보 | 사원조회(재직/퇴직, 상세 프로필) | ✅ 구현 | employees 조회, role별 스코프 |
| | | 사원등록/변경(신규입사, 인사이동, 퇴직) | ✅ 구현 | CRUD, EmployeeJobHistory, EmployeeStatusHistory |
| | 1-3 인사 Master 관리 | 코드관리(직급/직군, 근무형태 등) | ❌ 미구현 | CM_CODE_GROUP, CM_CODE, 직급·직군·근무형태 |
| | | 직무·직책 관리 | ❌ 미구현 | CM_JOB, CM_POS |
| **2. 근태관리** | 2-1 근태기본설정 | 근무체계, 근무일정, 휴가정책 | △ 부분 | WorkType만 있음, 휴가정책·근무일정 상세 없음 |
| | 2-2 근태입력·승인 | 출퇴근 기록 | ❌ 미구현 | TimeLog 테이블만 존재, 입력/조회 UI 없음 |
| | | 휴가신청·승인 | ✅ 구현 | LeaveRequest CRUD, approve/reject |
| | 2-3 근태마감 | 월간 근태집계 | ✅ 구현 | AttendanceMonthSummary, close-month |
| | | 급여연동 파일 생성 | ❌ 미구현 | 근태→급여 연동 파일 생성 기능 |
| **3. 급여·보상관리** | 3-1 급여기본설정 | 급여항목 | ✅ 구현 | PayItem CRUD |
| | | 세율·보험요율 | ❌ 미구현 | 세율·보험 설정 테이블/화면 |
| | 3-2 급여계산 | 대상자 확정, 근태반영, 시뮬레이션 | △ 부분 | calculate_payroll_run 있으나 단순 로직, 근태 연동 제한적 |
| | 3-3 급여지급·정산 | 명세서 | ❌ 미구현 | 급여명세서 생성/조회 |
| | | 은행이체 | ❌ 미구현 | PY_BANK_FILE, 이체 파일 생성 |
| | | 연말정산 | ❌ 미구현 | PY_YEAR_SETTLE |
| **4. 평가·승진관리** | 4-1 평가기준 설정 | 평가항목, 가중치 | ❌ 미구현 | EV_ITEM(평가항목), 항목별 가중치 |
| | 4-2 평가실행 | 대상자 설정 | ❌ 미구현 | EV_TARGET, EV_EVALUATOR |
| | | 자기평가 | ✅ 구현 | 단일 점수+코멘트만, 항목별 점수 없음 |
| | | 상사·다면평가 | ❌ 미구현 | 평가자별 점수 입력, 팀 평가 화면 |
| | 4-3 평가결과·승진연계 | 등급 산정 | ❌ 미구현 | EV_SUMMARY, GradePolicy, 등급 자동 산정 |
| | | 승진대상자 추천 | ❌ 미구현 | EV_PROMOTION_CANDIDATE |
| | | 이의신청 관리 | ❌ 미구현 | 평가 이의신청 프로세스 |
| **5. 교육·역량관리** | 5-1 교육과정 관리 | 과정 개설 | ✅ 구현 | TrainingCourse, TrainingSession |
| | | 대상자 선정, 자동 추천 | ❌ 미구현 | 역량 기반 추천 로직 |
| | 5-2 수강·이수 관리 | 교육신청, 이수처리 | △ 부분 | TrainingEnrollment 기본만, 이수처리 상태 변경 제한적 |
| | | 역량모델·역량진단 | ❌ 미구현 | TR_COMPETENCY_MODEL, TR_COMP_EVAL |
| **6. 복리후생관리** | 전체 | 복지포인트, 선택형 복리후생, 식대, 기숙사 | ❌ 미구현 | WF_BENEFIT_POLICY, WF_POINT_BALANCE, WF_POINT_TXN |
| **7. 보고서·대시보드** | 기본 KPI | 인력현황 요약 | △ 부분 | total/active employees, dept, pay_group, leave_pending |
| | | 이직률, 인건비, 근태·초과근로, 평가분포 | ❌ 미구현 | 상세 HR KPI 리포트 |
| **8. 시스템관리** | 8-1 사용자·조직권한 | 사용자 관리(계정 생성/잠금) | ✅ 구현 | User CRUD, 권한 요청/승인 |
| | | 조직·직무 기반 권한 | ❌ 미구현 | 조직/직무별 세분화 권한 |
| | 8-2 메뉴·역할권한 | 메뉴 구조, 역할별 메뉴권한 | ❌ 미구현 | SM_MENU, SM_ROLE_MENU_AUTH |
| | 8-3~8-9 | 보안·인증, 공통코드, 인터페이스, 로그·감사, 배치, 알림, 운영도구 | ❌ 미구현 | 해당 모듈 전체 |

---

## 2. DB 테이블별 구현 현황

| 매뉴얼 테이블 | 구현 테이블 | 상태 | 비고 |
|--------------|-------------|------|------|
| CM_DEPT | departments | ✅ | parent_id, effective_from/to, headcount_limit |
| CM_DEPT_HIST | - | ❌ | 조직 변경 이력 |
| CM_JOB, CM_POS | - | ❌ | 직무·직책 |
| CM_CODE_GROUP, CM_CODE | - | ❌ | 공통코드 |
| HR_EMP | employees | ✅ | user_id 추가됨 |
| HR_EMP_JOB_HIST | employee_job_histories | ✅ | 부서 변경 이력 |
| HR_EMP_STATUS_HIST | employee_status_histories | ✅ | 상태 변경 이력 |
| AT_WORK_CALENDAR | work_calendars | ✅ | 모델만 존재, UI 없음 |
| AT_WORK_TYPE | work_types | ✅ | |
| AT_WORK_SCHEDULE | work_schedules | ✅ | 모델만 존재 |
| AT_TIMELOG | time_logs | ✅ | 모델만 존재, UI 없음 |
| AT_LEAVE_REQ | leave_requests | ✅ | approver_emp_id, approved_at |
| AT_LEAVE_BALANCE | leave_balances | ✅ | 모델만 존재 |
| AT_MONTH_SUMMARY | attendance_month_summaries | ✅ | |
| PY_PAY_GROUP, PY_ITEM, PY_RUN, PY_RESULT, PY_RESULT_ITEM | pay_* | ✅ | |
| PY_BANK_FILE, PY_YEAR_SETTLE | - | ❌ | |
| EV_PLAN | evaluation_plans | ✅ | |
| EV_ITEM | - | ❌ | 평가항목 |
| EV_TARGET, EV_EVALUATOR | - | ❌ | 평가 대상·평가자 |
| EV_RESULT | evaluation_results | △ | 항목별 점수 없음, 단일 score만 |
| EV_SUMMARY | - | ❌ | 최종 등급 |
| EV_PROMOTION_CANDIDATE | - | ❌ | 승진후보 |
| TR_COURSE, TR_SESSION, TR_ENROLL | training_* | ✅ | |
| TR_COMPETENCY_MODEL, TR_COMP_EVAL | - | ❌ | |
| WF_* | - | ❌ | 복리후생 전체 |
| SM_USER | users | △ | SM_ROLE, SM_USER_ROLE 없음 |
| SM_MENU, SM_ROLE_MENU_AUTH | - | ❌ | |
| SM_LOGIN_LOG, SM_AUDIT_LOG | - | ❌ | |
| SM_IF_*, SM_BATCH_*, SM_MSG_* | - | ❌ | |

---

## 3. 우선 구현 권장 순서 (미구현 기능)

| 순위 | 영역 | 기능 | 난이도 | 비고 |
|------|------|------|--------|------|
| 1 | 평가 | 평가항목(EV_ITEM), 항목별 점수 | 중 | 평가 고도화 1차 |
| 2 | 평가 | 상사·다면평가, 팀 평가 화면 | 중 | 평가 고도화 2차 |
| 3 | 평가 | 등급 산정, 승진후보 | 중 | GradePolicy, aggregate |
| 4 | 교육 | 교육 UI(과정/회차/수강 목록) | 하 | 프론트 전용 |
| 5 | 복리후생 | 복지정책, 포인트 잔액/거래 | 중 | 신규 모듈 |
| 6 | 보고서 | 상세 KPI 리포트 | 중 | 이직률, 인건비 등 |
| 7 | 시스템 | 메뉴권한, 감사로그 | 중 | SM_MENU, SM_AUDIT_LOG |
| 8 | 근태 | 출퇴근 기록 UI | 하 | TimeLog 활용 |
| 9 | 급여 | 명세서, 은행이체 | 중 | |
| 10 | 조직 | 조직도 트리, 공통코드 | 중 | |

---

## 4. 요약 (업데이트)

- **구현 완료**: 조직·부서 기본, 사원 CRUD·이력, 근태(휴가·월집계·마감·출퇴근 기록), 급여 기본·계산, 평가 계획·자기평가·**항목별 점수·팀 평가·등급·승진후보**, 교육 기본·**과정/회차/수강 UI**, **복리후생(정책·잔액·거래)**, 사용자·권한 요청, **공통코드·감사로그 API**, **대시보드 KPI 확장(이직률·총급여)**
- **부분 구현**: 급여계산(단순 로직), 교육 이수처리(API만)
- **미구현**: 역량모델·역량진단, 상세 리포트(이직률·인건비 차트 등), 메뉴권한·배치·인터페이스
