import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Login from './Login'
import './App.css'

type Employee = {
  id: number
  emp_no: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  dept_id: number | null
  pay_group_id: number | null
  hire_date: string
  status: string
}

type Department = {
  id: number
  code: string
  name: string
}

type PayGroup = {
  id: number
  code: string
  name: string
  pay_cycle: string
  cutoff_day: number
  pay_day: number
}

type PayItem = {
  id: number
  code: string
  name: string
  item_type: string
  taxable: boolean
  calculation_type: string
  default_amount: number | null
}

type AttendanceSummary = {
  id: number
  emp_id: number
  year_month: string
  worked_hours: string
  overtime_hours: string
  late_count: number
  early_leave_count: number
  absence_count: number
}

type PayRun = {
  id: number
  pay_group_id: number
  year_month: string
  run_type: string
  status: string
}

type PayResult = {
  id: number
  emp_id: number
  gross_amount: string
  deduct_amount: string
  net_amount: string
  currency: string
  status: string
}

type WorkType = {
  id: number
  code: string
  name: string
  start_time: string
  end_time: string
  break_minutes: number
}

type LeaveRequest = {
  id: number
  emp_id: number
  leave_type: string
  start_datetime: string
  end_datetime: string
  hours: number
  status: string
  reason: string | null
}

type DashboardStats = {
  total_employees: number
  active_employees: number
  department_count: number
  pay_group_count: number
  pay_run_count: number
  leave_requests_pending: number
}

type User = {
  id: number
  username: string
  is_active: boolean
}

type TabKey = 'dashboard' | 'employees' | 'organization' | 'attendance' | 'payroll' | 'evaluation' | 'education' | 'users'

const API_BASE_STORAGE_KEY = 'jscorp_hr_api_base'

function getApiBase(): string {
  if (typeof window !== 'undefined') {
    const stored = window.localStorage.getItem(API_BASE_STORAGE_KEY)
    if (stored && String(stored).trim().length > 0) return String(stored).trim().replace(/\/$/, '')
  }
  const fromUrl = import.meta.env.VITE_API_BASE_URL
  if (fromUrl && String(fromUrl).trim().length > 0) return String(fromUrl).replace(/\/$/, '')
  const host = import.meta.env.VITE_API_HOST
  if (host && String(host).trim().length > 0) return `https://${String(host).trim()}`
  if (typeof window !== 'undefined' && window.location.hostname.endsWith('onrender.com')) {
    const h = window.location.hostname
    const origin = window.location.origin
    const withBackend = origin.replace(/-frontend\.onrender\.com$/, '-backend.onrender.com')
    if (withBackend !== origin) return withBackend
    if (!h.includes('-frontend')) return `https://${h.replace('.onrender.com', '-backend.onrender.com')}`
  }
  return 'http://localhost:8000'
}
const API_BASE = getApiBase()

function authHeaders(token: string | null): Record<string, string> {
  if (!token) return {}
  return { Authorization: `Bearer ${token}` }
}

async function fetchJson<T>(url: string, headers: Record<string, string> = {}): Promise<T> {
  const res = await fetch(url, { headers: { ...headers } })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || `Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

async function postJson<T>(
  url: string,
  body: object,
  headers: Record<string, string> = {},
): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || `Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

async function patchJson<T>(
  url: string,
  body: object,
  headers: Record<string, string> = {},
): Promise<T> {
  const res = await fetch(url, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || `Request failed: ${res.status}`)
  }
  return (await res.json()) as T
}

async function deleteReq(url: string, headers: Record<string, string> = {}): Promise<void> {
  const res = await fetch(url, { method: 'DELETE', headers: { ...headers } })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || `Request failed: ${res.status}`)
  }
}

const defaultEmpForm = {
  emp_no: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  hire_date: new Date().toISOString().slice(0, 10),
  status: 'ACTIVE',
  dept_id: null as number | null,
  pay_group_id: null as number | null,
}

const TOKEN_KEY = 'jscorp_hr_token'

function App() {
  const { t, i18n } = useTranslation()
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [activeTab, setActiveTab] = useState<TabKey>('dashboard')
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [payGroups, setPayGroups] = useState<PayGroup[]>([])
  const [payItems, setPayItems] = useState<PayItem[]>([])
  const [attendance, setAttendance] = useState<AttendanceSummary[]>([])
  const [payRuns, setPayRuns] = useState<PayRun[]>([])
  const [selectedRun, setSelectedRun] = useState<number | null>(null)
  const [payResults, setPayResults] = useState<PayResult[]>([])
  const [workTypes, setWorkTypes] = useState<WorkType[]>([])
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([])
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [showEmpModal, setShowEmpModal] = useState(false)
  const [editingEmp, setEditingEmp] = useState<Employee | null>(null)
  const [empForm, setEmpForm] = useState(defaultEmpForm)

  const [deleteTarget, setDeleteTarget] = useState<{ type: 'employee'; id: number } | null>(null)

  const [showDeptModal, setShowDeptModal] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [deptForm, setDeptForm] = useState({ code: '', name: '' })

  const [showPayGroupModal, setShowPayGroupModal] = useState(false)
  const [editingPayGroup, setEditingPayGroup] = useState<PayGroup | null>(null)
  const [payGroupForm, setPayGroupForm] = useState({
    code: '',
    name: '',
    pay_cycle: 'MONTHLY',
    cutoff_day: 25,
    pay_day: 10,
  })

  const [showPayRunModal, setShowPayRunModal] = useState(false)
  const [payRunForm, setPayRunForm] = useState({
    pay_group_id: 0,
    year_month: new Date().toISOString().slice(0, 7).replace('-', ''),
    run_type: 'REGULAR',
  })

  const [showWorkTypeModal, setShowWorkTypeModal] = useState(false)
  const [editingWorkType, setEditingWorkType] = useState<WorkType | null>(null)
  const [workTypeForm, setWorkTypeForm] = useState({
    code: '',
    name: '',
    start_time: '09:00',
    end_time: '18:00',
    break_minutes: 60,
  })

  const [showLeaveModal, setShowLeaveModal] = useState(false)
  const [leaveForm, setLeaveForm] = useState({
    emp_id: 0,
    leave_type: 'ANNUAL',
    start_datetime: '',
    end_datetime: '',
    hours: 8,
    reason: '',
  })

  const [showPayItemModal, setShowPayItemModal] = useState(false)
  const [editingPayItem, setEditingPayItem] = useState<PayItem | null>(null)
  const [payItemForm, setPayItemForm] = useState({
    code: '',
    name: '',
    item_type: 'EARNING',
    taxable: true,
    calculation_type: 'FIXED',
    default_amount: null as number | null,
  })

  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false)
  const [changePasswordForm, setChangePasswordForm] = useState({ current_password: '', new_password: '' })
  const [showAddUserModal, setShowAddUserModal] = useState(false)
  const [addUserForm, setAddUserForm] = useState({ username: '', password: '' })
  const [resetPasswordUserId, setResetPasswordUserId] = useState<number | null>(null)
  const [resetPasswordNew, setResetPasswordNew] = useState('')

  const currentYearMonth = new Date().toISOString().slice(0, 7).replace('-', '')

  const headers = authHeaders(token)

  const loadEmployees = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<Employee[]>(`${API_BASE}/api/employees`, headers)
    setEmployees(list)
  }, [token])

  const loadDepartments = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<Department[]>(`${API_BASE}/api/departments`, headers)
    setDepartments(list)
  }, [token])

  const loadPayGroups = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<PayGroup[]>(`${API_BASE}/api/payroll/pay-groups`, headers)
    setPayGroups(list)
  }, [token])

  const loadPayItems = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<PayItem[]>(`${API_BASE}/api/payroll/pay-items`, headers)
    setPayItems(list)
  }, [token])

  const loadAttendance = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<AttendanceSummary[]>(
      `${API_BASE}/api/attendance/monthly?year_month=${currentYearMonth}`,
      headers,
    )
    setAttendance(list)
  }, [token, currentYearMonth])

  const loadPayRuns = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<PayRun[]>(`${API_BASE}/api/payroll/runs`, headers)
    setPayRuns(list)
    if (list.length > 0) {
      setSelectedRun(list[0].id)
      const results = await fetchJson<PayResult[]>(
        `${API_BASE}/api/payroll/runs/${list[0].id}/results`,
        headers,
      )
      setPayResults(results)
    } else {
      setSelectedRun(null)
      setPayResults([])
    }
  }, [token])

  const loadDashboardStats = useCallback(async () => {
    if (!token) return
    const stats = await fetchJson<DashboardStats>(`${API_BASE}/api/dashboard/stats`, headers)
    setDashboardStats(stats)
  }, [token])

  const loadWorkTypes = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<WorkType[]>(`${API_BASE}/api/attendance/work-types`, headers)
    setWorkTypes(list)
  }, [token])

  const loadLeaveRequests = useCallback(async () => {
    if (!token) return
    const list = await fetchJson<LeaveRequest[]>(`${API_BASE}/api/attendance/leave-requests`, headers)
    setLeaveRequests(list)
  }, [token])

  const loadCurrentUser = useCallback(async () => {
    if (!token) return
    try {
      const me = await fetchJson<User>(`${API_BASE}/api/auth/me`, headers)
      setCurrentUser(me)
    } catch {
      setCurrentUser(null)
    }
  }, [token])

  const loadUsers = useCallback(async () => {
    if (!token) return
    try {
      const list = await fetchJson<User[]>(`${API_BASE}/api/users`, headers)
      setUsers(list)
    } catch {
      setUsers([])
    }
  }, [token])

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true)
        setError(null)
        await Promise.all([
          loadEmployees(),
          loadDepartments(),
          loadPayGroups(),
          loadPayItems(),
          loadAttendance(),
          loadPayRuns(),
          loadDashboardStats(),
          loadWorkTypes(),
          loadLeaveRequests(),
          loadCurrentUser(),
        ])
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load JSCORP HR data.')
      } finally {
        setLoading(false)
      }
    }
    void bootstrap()
  }, [loadEmployees, loadDepartments, loadPayGroups, loadPayItems, loadAttendance, loadPayRuns, loadDashboardStats, loadWorkTypes, loadLeaveRequests, loadCurrentUser])

  useEffect(() => {
    if (activeTab === 'users' && currentUser?.username === 'admin' && token) loadUsers()
  }, [activeTab, currentUser?.username, token, loadUsers])

  async function handleSelectRun(runId: number) {
    try {
      setSelectedRun(runId)
      setLoading(true)
      const results = await fetchJson<PayResult[]>(
        `${API_BASE}/api/payroll/runs/${runId}/results`,
        headers,
      )
      setPayResults(results)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load payroll results.')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <Login
        apiBase={API_BASE}
        onSuccess={(tkn) => {
          localStorage.setItem(TOKEN_KEY, tkn)
          setToken(tkn)
        }}
      />
    )
  }

  function openAddEmployee() {
    setEditingEmp(null)
    setEmpForm(defaultEmpForm)
    setShowEmpModal(true)
  }

  function openEditEmployee(emp: Employee) {
    setEditingEmp(emp)
    setEmpForm({
      emp_no: emp.emp_no,
      first_name: emp.first_name,
      last_name: emp.last_name,
      email: emp.email,
      phone: emp.phone || '',
      hire_date: emp.hire_date.slice(0, 10),
      status: emp.status,
      dept_id: emp.dept_id,
      pay_group_id: emp.pay_group_id,
    })
    setShowEmpModal(true)
  }

  async function submitEmployee() {
    try {
      setError(null)
      if (editingEmp) {
        await patchJson(
          `${API_BASE}/api/employees/${editingEmp.id}`,
          {
            emp_no: empForm.emp_no,
            first_name: empForm.first_name,
            last_name: empForm.last_name,
            email: empForm.email,
            phone: empForm.phone || null,
            hire_date: empForm.hire_date,
            status: empForm.status,
            dept_id: empForm.dept_id,
            pay_group_id: empForm.pay_group_id,
          },
          headers,
        )
      } else {
        await postJson(
          `${API_BASE}/api/employees`,
          {
            ...empForm,
            phone: empForm.phone || null,
            dept_id: empForm.dept_id,
            pay_group_id: empForm.pay_group_id,
          },
          headers,
        )
      }
      setShowEmpModal(false)
      await loadEmployees()
      await loadAttendance()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed.')
    }
  }

  async function confirmDeleteEmployee() {
    if (!deleteTarget || deleteTarget.type !== 'employee') return
    try {
      setError(null)
      await deleteReq(`${API_BASE}/api/employees/${deleteTarget.id}`, headers)
      setDeleteTarget(null)
      await loadEmployees()
      await loadAttendance()
      await loadPayRuns()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed.')
    }
  }

  function openAddDept() {
    setEditingDept(null)
    setDeptForm({ code: '', name: '' })
    setShowDeptModal(true)
  }

  function openEditDept(d: Department) {
    setEditingDept(d)
    setDeptForm({ code: d.code, name: d.name })
    setShowDeptModal(true)
  }

  async function submitDepartment() {
    try {
      setError(null)
      if (editingDept) {
        await patchJson(
          `${API_BASE}/api/departments/${editingDept.id}`,
          deptForm,
          headers,
        )
      } else {
        await postJson(`${API_BASE}/api/departments`, deptForm, headers)
      }
      setShowDeptModal(false)
      await loadDepartments()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed.')
    }
  }

  function openAddPayGroup() {
    setEditingPayGroup(null)
    setPayGroupForm({
      code: '',
      name: '',
      pay_cycle: 'MONTHLY',
      cutoff_day: 25,
      pay_day: 10,
    })
    setShowPayGroupModal(true)
  }

  function openEditPayGroup(pg: PayGroup) {
    setEditingPayGroup(pg)
    setPayGroupForm({
      code: pg.code,
      name: pg.name,
      pay_cycle: pg.pay_cycle,
      cutoff_day: pg.cutoff_day,
      pay_day: pg.pay_day,
    })
    setShowPayGroupModal(true)
  }

  async function submitPayGroup() {
    try {
      setError(null)
      if (editingPayGroup) {
        await patchJson(
          `${API_BASE}/api/payroll/pay-groups/${editingPayGroup.id}`,
          payGroupForm,
          headers,
        )
      } else {
        await postJson(`${API_BASE}/api/payroll/pay-groups`, payGroupForm, headers)
      }
      setShowPayGroupModal(false)
      await loadPayGroups()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed.')
    }
  }

  async function submitPayRun() {
    try {
      setError(null)
      await postJson(`${API_BASE}/api/payroll/runs`, payRunForm, headers)
      setShowPayRunModal(false)
      setPayRunForm({
        pay_group_id: payGroups[0]?.id ?? 0,
        year_month: new Date().toISOString().slice(0, 7).replace('-', ''),
        run_type: 'REGULAR',
      })
      await loadPayRuns()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Create payroll run failed.')
    }
  }

  function openAddWorkType() {
    setEditingWorkType(null)
    setWorkTypeForm({ code: '', name: '', start_time: '09:00', end_time: '18:00', break_minutes: 60 })
    setShowWorkTypeModal(true)
  }

  function openEditWorkType(wt: WorkType) {
    setEditingWorkType(wt)
    setWorkTypeForm({ code: wt.code, name: wt.name, start_time: wt.start_time, end_time: wt.end_time, break_minutes: wt.break_minutes })
    setShowWorkTypeModal(true)
  }

  async function submitWorkType() {
    try {
      setError(null)
      if (editingWorkType) {
        await patchJson(`${API_BASE}/api/attendance/work-types/${editingWorkType.id}`, workTypeForm, headers)
      } else {
        await postJson(`${API_BASE}/api/attendance/work-types`, workTypeForm, headers)
      }
      setShowWorkTypeModal(false)
      await loadWorkTypes()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed.')
    }
  }

  function openLeaveRequest() {
    setLeaveForm({
      emp_id: employees[0]?.id ?? 0,
      leave_type: 'ANNUAL',
      start_datetime: '',
      end_datetime: '',
      hours: 8,
      reason: '',
    })
    setShowLeaveModal(true)
  }

  async function submitLeaveRequest() {
    try {
      setError(null)
      if (!leaveForm.start_datetime || !leaveForm.end_datetime) {
        setError('Start and end datetime required.')
        return
      }
      const start = new Date(leaveForm.start_datetime).toISOString()
      const end = new Date(leaveForm.end_datetime).toISOString()
      await postJson(`${API_BASE}/api/attendance/leave-requests`, {
        emp_id: leaveForm.emp_id,
        leave_type: leaveForm.leave_type,
        start_datetime: start,
        end_datetime: end,
        hours: leaveForm.hours,
        reason: leaveForm.reason || null,
      }, headers)
      setShowLeaveModal(false)
      await loadLeaveRequests()
      await loadDashboardStats()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Request failed.')
    }
  }

  function openAddPayItem() {
    setEditingPayItem(null)
    setPayItemForm({ code: '', name: '', item_type: 'EARNING', taxable: true, calculation_type: 'FIXED', default_amount: null })
    setShowPayItemModal(true)
  }

  function openEditPayItem(pi: PayItem) {
    setEditingPayItem(pi)
    setPayItemForm({
      code: pi.code,
      name: pi.name,
      item_type: pi.item_type,
      taxable: pi.taxable,
      calculation_type: pi.calculation_type,
      default_amount: pi.default_amount,
    })
    setShowPayItemModal(true)
  }

  async function submitPayItem() {
    try {
      setError(null)
      const body = { ...payItemForm, default_amount: payItemForm.default_amount }
      if (editingPayItem) {
        await patchJson(`${API_BASE}/api/payroll/pay-items/${editingPayItem.id}`, body, headers)
      } else {
        await postJson(`${API_BASE}/api/payroll/pay-items`, body, headers)
      }
      setShowPayItemModal(false)
      await loadPayItems()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed.')
    }
  }

  async function submitChangePassword() {
    try {
      setError(null)
      await postJson(`${API_BASE}/api/auth/change-password`, changePasswordForm, headers)
      setShowChangePasswordModal(false)
      setChangePasswordForm({ current_password: '', new_password: '' })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.')
    }
  }

  async function submitAddUser() {
    try {
      setError(null)
      await postJson(`${API_BASE}/api/users`, addUserForm, headers)
      setShowAddUserModal(false)
      setAddUserForm({ username: '', password: '' })
      await loadUsers()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.')
    }
  }

  async function submitResetPassword() {
    if (resetPasswordUserId == null) return
    try {
      setError(null)
      await patchJson(`${API_BASE}/api/users/${resetPasswordUserId}/password`, { new_password: resetPasswordNew }, headers)
      setResetPasswordUserId(null)
      setResetPasswordNew('')
      await loadUsers()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed.')
    }
  }

  const activeEmpCount = employees.filter((e) => e.status === 'ACTIVE').length

  return (
    <div className="app-shell">
      <div className="card-surface">
        <header className="app-header">
          <div className="app-brand">
            <div className="brand-badge">JS</div>
            <div>
              <div className="brand-text-main">{t('app.title')}</div>
              <div className="brand-text-sub">{t('app.subtitle')}</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              type="button"
              className="btn-secondary"
              style={{
                padding: '0.25rem 0.5rem',
                fontSize: '0.75rem',
                fontWeight: i18n.language === 'ko' ? 600 : 400,
              }}
              onClick={() => i18n.changeLanguage('ko')}
            >
              KO
            </button>
            <button
              type="button"
              className="btn-secondary"
              style={{
                padding: '0.25rem 0.5rem',
                fontSize: '0.75rem',
                fontWeight: i18n.language === 'en' ? 600 : 400,
              }}
              onClick={() => i18n.changeLanguage('en')}
            >
              EN
            </button>
            <button
              type="button"
              className="btn-secondary"
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
              onClick={() => { setChangePasswordForm({ current_password: '', new_password: '' }); setShowChangePasswordModal(true) }}
            >
              {t('auth.changePassword')}
            </button>
            <button
              type="button"
              className="btn-danger"
              style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
              onClick={() => {
                localStorage.removeItem(TOKEN_KEY)
                setToken(null)
              }}
            >
              {t('nav.logout')}
            </button>
          </div>
        </header>

        <nav className="tab-nav" aria-label="Main modules">
          <button
            type="button"
            className={`tab-pill ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="pill-dot" />
            {t('nav.dashboard')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'employees' ? 'active' : ''}`}
            onClick={() => setActiveTab('employees')}
          >
            <span className="pill-dot" />
            {t('nav.employees')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'organization' ? 'active' : ''}`}
            onClick={() => setActiveTab('organization')}
          >
            <span className="pill-dot" />
            {t('nav.organization')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'attendance' ? 'active' : ''}`}
            onClick={() => setActiveTab('attendance')}
          >
            <span className="pill-dot" />
            {t('nav.attendance')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'payroll' ? 'active' : ''}`}
            onClick={() => setActiveTab('payroll')}
          >
            <span className="pill-dot" />
            {t('nav.payroll')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'evaluation' ? 'active' : ''}`}
            onClick={() => setActiveTab('evaluation')}
          >
            <span className="pill-dot" />
            {t('nav.evaluation')}
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'education' ? 'active' : ''}`}
            onClick={() => setActiveTab('education')}
          >
            <span className="pill-dot" />
            {t('nav.education')}
          </button>
          {currentUser?.username === 'admin' && (
            <button
              type="button"
              className={`tab-pill ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              <span className="pill-dot" />
              {t('nav.users')}
            </button>
          )}
        </nav>

        {loading && (
          <div className="section-subtitle" style={{ marginBottom: '0.6rem' }}>
            {t('common.loading')}
          </div>
        )}
        {error && (
          <div className="section-subtitle" style={{ color: '#fecaca', marginBottom: '0.6rem' }}>
            {error}
          </div>
        )}

        {activeTab === 'dashboard' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('dashboard.title')}</div>
                <div className="section-subtitle">{t('dashboard.subtitle')}</div>
              </div>
            </div>
            {dashboardStats && (
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.totalEmployees')}</div>
                  <div className="kpi-main">{dashboardStats.total_employees}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.activeEmployees')}</div>
                  <div className="kpi-main">{dashboardStats.active_employees}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.departments')}</div>
                  <div className="kpi-main">{dashboardStats.department_count}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.payGroups')}</div>
                  <div className="kpi-main">{dashboardStats.pay_group_count}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.payRuns')}</div>
                  <div className="kpi-main">{dashboardStats.pay_run_count}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('dashboard.leavePending')}</div>
                  <div className="kpi-main">{dashboardStats.leave_requests_pending}</div>
                </div>
              </div>
            )}
          </section>
        )}

        {activeTab === 'employees' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('employees.title')}</div>
                <div className="section-subtitle">{t('employees.subtitle')}</div>
              </div>
            </div>
            <div className="chip-row">
              <span className="chip soft">{t('employees.active')} {activeEmpCount}</span>
              <span className="chip">{t('employees.total')} {employees.length}</span>
            </div>
            <div className="list-card">
              <div className="list-header">
                <span>{t('payroll.employee')}</span>
                <span>{t('common.actions')}</span>
              </div>
              {employees.map((emp) => (
                <div key={emp.id} className="list-row">
                  <div className="list-row-main">
                    <div className="list-title">
                      {emp.first_name} {emp.last_name}
                    </div>
                    <div className="list-meta">
                      {emp.emp_no} · {emp.email}
                    </div>
                  </div>
                  <div className="list-value list-row-actions">
                    <button type="button" onClick={() => openEditEmployee(emp)}>
                      {t('employees.edit')}
                    </button>
                    <button
                      type="button"
                      className="btn-danger"
                      onClick={() => setDeleteTarget({ type: 'employee', id: emp.id })}
                    >
                      {t('employees.delete')}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="section-footer">
              <span>{t('employees.manageHint')}</span>
              <button type="button" className="primary-button" onClick={openAddEmployee}>
                {t('employees.add')}
              </button>
            </div>
          </section>
        )}

        {activeTab === 'organization' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('organization.title')}</div>
                <div className="section-subtitle">{t('organization.subtitle')}</div>
              </div>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('organization.departments')}</div>
              <div className="list-card">
                {departments.map((d) => (
                  <div key={d.id} className="list-row">
                    <div className="list-row-main">
                      <div className="list-title">{d.name}</div>
                      <div className="list-meta">{d.code}</div>
                    </div>
                    <div className="list-row-actions">
                      <button type="button" onClick={() => openEditDept(d)}>{t('employees.edit')}</button>
                      <button
                        type="button"
                        className="btn-danger"
                        onClick={async () => {
                          try {
                            await deleteReq(`${API_BASE}/api/departments/${d.id}`, headers)
                            await loadDepartments()
                          } catch (e) {
                            setError(e instanceof Error ? e.message : 'Delete failed.')
                          }
                        }}
                      >
                        {t('employees.delete')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button type="button" className="primary-button" onClick={openAddDept} style={{ marginTop: '0.5rem' }}>
                {t('organization.addDepartment')}
              </button>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('organization.payGroups')}</div>
              <div className="list-card">
                {payGroups.map((pg) => (
                  <div key={pg.id} className="list-row">
                    <div className="list-row-main">
                      <div className="list-title">{pg.name}</div>
                      <div className="list-meta">{pg.code} · {pg.pay_cycle}</div>
                    </div>
                    <div className="list-row-actions">
                      <button type="button" onClick={() => openEditPayGroup(pg)}>{t('employees.edit')}</button>
                      <button
                        type="button"
                        className="btn-danger"
                        onClick={async () => {
                          try {
                            await deleteReq(
                              `${API_BASE}/api/payroll/pay-groups/${pg.id}`,
                              headers,
                            )
                            await loadPayGroups()
                          } catch (e) {
                            setError(e instanceof Error ? e.message : 'Delete failed.')
                          }
                        }}
                      >
                        {t('employees.delete')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button type="button" className="primary-button" onClick={openAddPayGroup} style={{ marginTop: '0.5rem' }}>
                {t('organization.addPayGroup')}
              </button>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('organization.payItems')}</div>
              <div className="list-card">
                {payItems.map((pi) => (
                  <div key={pi.id} className="list-row">
                    <div className="list-row-main">
                      <div className="list-title">{pi.name}</div>
                      <div className="list-meta">{pi.code} · {pi.item_type} · {pi.calculation_type}</div>
                    </div>
                    <div className="list-row-actions">
                      <button type="button" onClick={() => openEditPayItem(pi)}>{t('employees.edit')}</button>
                      <button type="button" className="btn-danger" onClick={async () => { try { await deleteReq(`${API_BASE}/api/payroll/pay-items/${pi.id}`, headers); await loadPayItems() } catch (e) { setError(e instanceof Error ? e.message : 'Delete failed.') } }}>{t('employees.delete')}</button>
                    </div>
                  </div>
                ))}
              </div>
              <button type="button" className="primary-button" onClick={openAddPayItem} style={{ marginTop: '0.5rem' }}>
                {t('organization.addPayItem')}
              </button>
            </div>
          </section>
        )}

        {activeTab === 'attendance' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('attendance.title')}</div>
                <div className="section-subtitle">
                  {currentYearMonth.slice(0, 4)}-{currentYearMonth.slice(4)}
                </div>
              </div>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('attendance.workTypes')}</div>
              <div className="list-card">
                {workTypes.map((wt) => (
                  <div key={wt.id} className="list-row">
                    <div className="list-row-main">
                      <div className="list-title">{wt.name}</div>
                      <div className="list-meta">{wt.code} · {wt.start_time}–{wt.end_time} · {wt.break_minutes}m break</div>
                    </div>
                    <div className="list-row-actions">
                      <button type="button" onClick={() => openEditWorkType(wt)}>{t('employees.edit')}</button>
                      <button type="button" className="btn-danger" onClick={async () => { try { await deleteReq(`${API_BASE}/api/attendance/work-types/${wt.id}`, headers); await loadWorkTypes() } catch (e) { setError(e instanceof Error ? e.message : 'Delete failed.') } }}>{t('employees.delete')}</button>
                    </div>
                  </div>
                ))}
              </div>
              <button type="button" className="primary-button" onClick={openAddWorkType} style={{ marginTop: '0.5rem' }}>
                {t('attendance.addWorkType')}
              </button>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('attendance.leaveRequests')}</div>
              <div className="list-card">
                <div className="list-header">
                  <span>{t('payroll.employee')}</span>
                  <span>{t('attendance.leaveType')} · {t('attendance.hours')}</span>
                </div>
                {leaveRequests.map((lr) => {
                  const emp = employees.find((e) => e.id === lr.emp_id)
                  return (
                    <div key={lr.id} className="list-row">
                      <div className="list-row-main">
                        <div className="list-title">{emp ? `${emp.first_name} ${emp.last_name}` : `Emp #${lr.emp_id}`}</div>
                        <div className="list-meta">{lr.start_datetime.slice(0, 16)} – {lr.end_datetime.slice(0, 16)}</div>
                      </div>
                      <div className="list-value">
                        <span className="badge-soft">{lr.leave_type}</span> · {lr.hours}h · {lr.status}
                      </div>
                    </div>
                  )
                })}
              </div>
              <button type="button" className="primary-button" onClick={openLeaveRequest} style={{ marginTop: '0.5rem' }}>
                {t('attendance.requestLeave')}
              </button>
            </div>
            <div className="sub-section">
              <div className="sub-section-title">{t('attendance.monthlySummary')}</div>
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-label">{t('attendance.employees')}</div>
                  <div className="kpi-main">{employees.length}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">{t('attendance.tracked')}</div>
                  <div className="kpi-main">{attendance.length}</div>
                </div>
              </div>
              <div className="list-card">
                <div className="list-header">
                  <span>{t('payroll.employee')}</span>
                  <span>{t('attendance.hoursIssues')}</span>
                </div>
                {attendance.map((row) => {
                  const emp = employees.find((e) => e.id === row.emp_id)
                  const issues = row.late_count + row.early_leave_count + row.absence_count
                  return (
                    <div key={row.id} className="list-row">
                      <div className="list-row-main">
                        <div className="list-title">
                          {emp ? `${emp.first_name} ${emp.last_name}` : `Emp #${row.emp_id}`}
                        </div>
                        <div className="list-meta">
                          {t('attendance.worked')} {row.worked_hours}h · {t('attendance.overtime')} {row.overtime_hours}h
                        </div>
                      </div>
                      <div className="list-value">
                        <span className={`badge-soft ${issues > 0 ? 'warning' : ''}`}>
                          {issues > 0 ? t('attendance.issues', { count: issues }) : t('attendance.clean')}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </section>
        )}

        {activeTab === 'payroll' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('payroll.title')}</div>
                <div className="section-subtitle">{t('payroll.subtitle')}</div>
              </div>
            </div>
            <div className="list-card" style={{ marginBottom: '0.7rem' }}>
              <div className="list-header">
                <span>{t('payroll.period')}</span>
                <span>{t('payroll.status')}</span>
              </div>
              {payRuns.map((run) => (
                <button
                  key={run.id}
                  type="button"
                  className="list-row"
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: 'transparent',
                    border: 'none',
                    paddingInline: 0,
                    cursor: 'pointer',
                  }}
                  onClick={() => handleSelectRun(run.id)}
                >
                  <div className="list-row-main">
                    <div className="list-title">
                      {run.year_month.slice(0, 4)}-{run.year_month.slice(4)} · {run.run_type}
                    </div>
                    <div className="list-meta">Pay group #{run.pay_group_id}</div>
                  </div>
                  <div className="list-value">
                    <span className="badge-soft">{run.status}</span>
                  </div>
                </button>
              ))}
            </div>
            {selectedRun && (
              <div className="list-card">
                <div className="list-header">
                  <span>{t('payroll.employee')}</span>
                  <span>{t('payroll.netPay')}</span>
                </div>
                {payResults.map((res) => {
                  const emp = employees.find((e) => e.id === res.emp_id)
                  return (
                    <div key={res.id} className="list-row">
                      <div className="list-row-main">
                        <div className="list-title">
                          {emp ? `${emp.first_name} ${emp.last_name}` : `Emp #${res.emp_id}`}
                        </div>
                        <div className="list-meta">
                          {t('payroll.gross')} {Number(res.gross_amount).toLocaleString()} · {t('payroll.deduct')}{' '}
                          {Number(res.deduct_amount).toLocaleString()}
                        </div>
                      </div>
                      <div className="list-value">
                        {Number(res.net_amount).toLocaleString()} {res.currency}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
            <div className="section-footer">
              <span>{t('payroll.newRunHint')}</span>
              <button
                type="button"
                className="primary-button"
                onClick={() => {
                  setPayRunForm({
                    pay_group_id: payGroups[0]?.id ?? 0,
                    year_month: new Date().toISOString().slice(0, 7).replace('-', ''),
                    run_type: 'REGULAR',
                  })
                  setShowPayRunModal(true)
                }}
              >
                {t('payroll.newRun')}
              </button>
            </div>
          </section>
        )}

        {activeTab === 'evaluation' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('evaluation.title')}</div>
                <div className="section-subtitle">{t('evaluation.subtitle')}</div>
              </div>
            </div>
            <p className="section-subtitle" style={{ marginTop: '1rem' }}>{t('evaluation.comingSoon')}</p>
          </section>
        )}

        {activeTab === 'education' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('education.title')}</div>
                <div className="section-subtitle">{t('education.subtitle')}</div>
              </div>
            </div>
            <p className="section-subtitle" style={{ marginTop: '1rem' }}>{t('education.comingSoon')}</p>
          </section>
        )}

        {activeTab === 'users' && currentUser?.username === 'admin' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">{t('auth.users')}</div>
                <div className="section-subtitle">{t('auth.usersSubtitle')}</div>
              </div>
            </div>
            <div className="list-card">
              <div className="list-header">
                <span>{t('auth.username')}</span>
                <span>{t('common.actions')}</span>
              </div>
              {users.map((u) => (
                <div key={u.id} className="list-row">
                  <div className="list-row-main">
                    <div className="list-title">{u.username}</div>
                    <div className="list-meta">{u.is_active ? t('auth.active') : t('auth.inactive')}</div>
                  </div>
                  <div className="list-row-actions">
                    <button
                      type="button"
                      onClick={() => { setResetPasswordUserId(u.id); setResetPasswordNew('') }}
                    >
                      {t('auth.resetPassword')}
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="section-footer">
              <span>{t('auth.addUserHint')}</span>
              <button type="button" className="primary-button" onClick={() => { setAddUserForm({ username: '', password: '' }); setShowAddUserModal(true) }}>
                {t('auth.addUser')}
              </button>
            </div>
          </section>
        )}
      </div>

      {/* Employee add/edit modal */}
      {showEmpModal && (
        <div className="modal-overlay" onClick={() => setShowEmpModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {editingEmp ? t('employees.editEmployee') : t('employees.addEmployee')}
            </div>
            <div className="form-row">
              <label>{t('employees.employeeNo')}</label>
              <input
                value={empForm.emp_no}
                onChange={(e) => setEmpForm((f) => ({ ...f, emp_no: e.target.value }))}
                placeholder="E0001"
              />
            </div>
            <div className="form-row">
              <label>{t('employees.firstName')}</label>
              <input
                value={empForm.first_name}
                onChange={(e) => setEmpForm((f) => ({ ...f, first_name: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('employees.lastName')}</label>
              <input
                value={empForm.last_name}
                onChange={(e) => setEmpForm((f) => ({ ...f, last_name: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('employees.email')}</label>
              <input
                type="email"
                value={empForm.email}
                onChange={(e) => setEmpForm((f) => ({ ...f, email: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('employees.phone')}</label>
              <input
                value={empForm.phone}
                onChange={(e) => setEmpForm((f) => ({ ...f, phone: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('employees.hireDate')}</label>
              <input
                type="date"
                value={empForm.hire_date}
                onChange={(e) => setEmpForm((f) => ({ ...f, hire_date: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('employees.status')}</label>
              <select
                value={empForm.status}
                onChange={(e) => setEmpForm((f) => ({ ...f, status: e.target.value }))}
              >
                <option value="ACTIVE">ACTIVE</option>
                <option value="INACTIVE">INACTIVE</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('employees.department')}</label>
              <select
                value={empForm.dept_id ?? ''}
                onChange={(e) =>
                  setEmpForm((f) => ({
                    ...f,
                    dept_id: e.target.value ? Number(e.target.value) : null,
                  }))
                }
              >
                <option value="">—</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.code})
                  </option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <label>{t('employees.payGroup')}</label>
              <select
                value={empForm.pay_group_id ?? ''}
                onChange={(e) =>
                  setEmpForm((f) => ({
                    ...f,
                    pay_group_id: e.target.value ? Number(e.target.value) : null,
                  }))
                }
              >
                <option value="">—</option>
                {payGroups.map((pg) => (
                  <option key={pg.id} value={pg.id}>
                    {pg.name} ({pg.code})
                  </option>
                ))}
              </select>
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowEmpModal(false)}>
                {t('employees.cancel')}
              </button>
              <button type="button" className="primary-button" onClick={submitEmployee}>
                {editingEmp ? t('employees.save') : t('employees.addBtn')}
              </button>
            </div>
          </div>
        </div>
      )}

      {deleteTarget && deleteTarget.type === 'employee' && (
        <div className="modal-overlay" onClick={() => setDeleteTarget(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('employees.deleteConfirm')}</div>
            <p style={{ fontSize: '0.9rem', color: '#9ca3af', marginBottom: '1rem' }}>
              {t('employees.deleteConfirmHint')}
            </p>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setDeleteTarget(null)}>
                {t('employees.cancel')}
              </button>
              <button type="button" className="btn-danger" onClick={confirmDeleteEmployee}>
                {t('employees.delete')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeptModal && (
        <div className="modal-overlay" onClick={() => setShowDeptModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {editingDept ? t('organization.editDepartment') : t('organization.addDepartmentTitle')}
            </div>
            <div className="form-row">
              <label>{t('organization.code')}</label>
              <input
                value={deptForm.code}
                onChange={(e) => setDeptForm((f) => ({ ...f, code: e.target.value }))}
                placeholder="HQ"
              />
            </div>
            <div className="form-row">
              <label>{t('organization.name')}</label>
              <input
                value={deptForm.name}
                onChange={(e) => setDeptForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Headquarters"
              />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowDeptModal(false)}>
                {t('employees.cancel')}
              </button>
              <button type="button" className="primary-button" onClick={submitDepartment}>
                {editingDept ? t('employees.save') : t('employees.addBtn')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showPayGroupModal && (
        <div className="modal-overlay" onClick={() => setShowPayGroupModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {editingPayGroup ? t('organization.editPayGroup') : t('organization.addPayGroupTitle')}
            </div>
            <div className="form-row">
              <label>{t('organization.code')}</label>
              <input
                value={payGroupForm.code}
                onChange={(e) => setPayGroupForm((f) => ({ ...f, code: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('organization.name')}</label>
              <input
                value={payGroupForm.name}
                onChange={(e) => setPayGroupForm((f) => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div className="form-row">
              <label>{t('organization.payCycle')}</label>
              <select
                value={payGroupForm.pay_cycle}
                onChange={(e) => setPayGroupForm((f) => ({ ...f, pay_cycle: e.target.value }))}
              >
                <option value="MONTHLY">{t('payroll.MONTHLY')}</option>
                <option value="WEEKLY">{t('payroll.WEEKLY')}</option>
                <option value="BIWEEKLY">{t('payroll.BIWEEKLY')}</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('organization.cutoffDay')}</label>
              <input
                type="number"
                min={1}
                max={31}
                value={payGroupForm.cutoff_day}
                onChange={(e) =>
                  setPayGroupForm((f) => ({ ...f, cutoff_day: Number(e.target.value) || 25 }))
                }
              />
            </div>
            <div className="form-row">
              <label>{t('organization.payDay')}</label>
              <input
                type="number"
                min={1}
                max={31}
                value={payGroupForm.pay_day}
                onChange={(e) =>
                  setPayGroupForm((f) => ({ ...f, pay_day: Number(e.target.value) || 10 }))
                }
              />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowPayGroupModal(false)}>
                {t('employees.cancel')}
              </button>
              <button type="button" className="primary-button" onClick={submitPayGroup}>
                {editingPayGroup ? t('employees.save') : t('employees.addBtn')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showPayRunModal && (
        <div className="modal-overlay" onClick={() => setShowPayRunModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('payroll.newPayRunTitle')}</div>
            <div className="form-row">
              <label>{t('employees.payGroup')}</label>
              <select
                value={payRunForm.pay_group_id || ''}
                onChange={(e) =>
                  setPayRunForm((f) => ({ ...f, pay_group_id: Number(e.target.value) }))
                }
              >
                {payGroups.map((pg) => (
                  <option key={pg.id} value={pg.id}>
                    {pg.name} ({pg.code})
                  </option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <label>{t('payroll.yearMonth')}</label>
              <input
                value={payRunForm.year_month}
                onChange={(e) => setPayRunForm((f) => ({ ...f, year_month: e.target.value }))}
                placeholder="202502"
              />
            </div>
            <div className="form-row">
              <label>{t('payroll.runType')}</label>
              <select
                value={payRunForm.run_type}
                onChange={(e) => setPayRunForm((f) => ({ ...f, run_type: e.target.value }))}
              >
                <option value="REGULAR">{t('payroll.REGULAR')}</option>
                <option value="BONUS">{t('payroll.BONUS')}</option>
                <option value="SEVERANCE">{t('payroll.SEVERANCE')}</option>
              </select>
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowPayRunModal(false)}>
                {t('employees.cancel')}
              </button>
              <button type="button" className="primary-button" onClick={submitPayRun}>
                {t('payroll.create')}
              </button>
            </div>
          </div>
        </div>
      )}

      {showWorkTypeModal && (
        <div className="modal-overlay" onClick={() => setShowWorkTypeModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {editingWorkType ? t('attendance.editWorkType') : t('attendance.addWorkType')}
            </div>
            <div className="form-row">
              <label>{t('organization.code')}</label>
              <input value={workTypeForm.code} onChange={(e) => setWorkTypeForm((f) => ({ ...f, code: e.target.value }))} placeholder="DAY" />
            </div>
            <div className="form-row">
              <label>{t('organization.name')}</label>
              <input value={workTypeForm.name} onChange={(e) => setWorkTypeForm((f) => ({ ...f, name: e.target.value }))} placeholder="Day shift" />
            </div>
            <div className="form-row">
              <label>{t('attendance.startTime')}</label>
              <input type="time" value={workTypeForm.start_time} onChange={(e) => setWorkTypeForm((f) => ({ ...f, start_time: e.target.value }))} />
            </div>
            <div className="form-row">
              <label>{t('attendance.endTime')}</label>
              <input type="time" value={workTypeForm.end_time} onChange={(e) => setWorkTypeForm((f) => ({ ...f, end_time: e.target.value }))} />
            </div>
            <div className="form-row">
              <label>{t('attendance.breakMinutes')}</label>
              <input type="number" min={0} value={workTypeForm.break_minutes} onChange={(e) => setWorkTypeForm((f) => ({ ...f, break_minutes: Number(e.target.value) || 0 }))} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowWorkTypeModal(false)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitWorkType}>{editingWorkType ? t('employees.save') : t('employees.addBtn')}</button>
            </div>
          </div>
        </div>
      )}

      {showLeaveModal && (
        <div className="modal-overlay" onClick={() => setShowLeaveModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('attendance.requestLeave')}</div>
            <div className="form-row">
              <label>{t('payroll.employee')}</label>
              <select value={leaveForm.emp_id || ''} onChange={(e) => setLeaveForm((f) => ({ ...f, emp_id: Number(e.target.value) }))}>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name} ({emp.emp_no})</option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <label>{t('attendance.leaveType')}</label>
              <select value={leaveForm.leave_type} onChange={(e) => setLeaveForm((f) => ({ ...f, leave_type: e.target.value }))}>
                <option value="ANNUAL">ANNUAL</option>
                <option value="SICK">SICK</option>
                <option value="SPECIAL">SPECIAL</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('attendance.startDatetime')}</label>
              <input type="datetime-local" value={leaveForm.start_datetime} onChange={(e) => setLeaveForm((f) => ({ ...f, start_datetime: e.target.value }))} />
            </div>
            <div className="form-row">
              <label>{t('attendance.endDatetime')}</label>
              <input type="datetime-local" value={leaveForm.end_datetime} onChange={(e) => setLeaveForm((f) => ({ ...f, end_datetime: e.target.value }))} />
            </div>
            <div className="form-row">
              <label>{t('attendance.hours')}</label>
              <input type="number" min={0} step={0.5} value={leaveForm.hours} onChange={(e) => setLeaveForm((f) => ({ ...f, hours: Number(e.target.value) || 0 }))} />
            </div>
            <div className="form-row">
              <label>{t('attendance.reason')}</label>
              <input value={leaveForm.reason} onChange={(e) => setLeaveForm((f) => ({ ...f, reason: e.target.value }))} placeholder="" />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowLeaveModal(false)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitLeaveRequest}>{t('attendance.submitRequest')}</button>
            </div>
          </div>
        </div>
      )}

      {showPayItemModal && (
        <div className="modal-overlay" onClick={() => setShowPayItemModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">
              {editingPayItem ? t('organization.editPayItem') : t('organization.addPayItemTitle')}
            </div>
            <div className="form-row">
              <label>{t('organization.code')}</label>
              <input value={payItemForm.code} onChange={(e) => setPayItemForm((f) => ({ ...f, code: e.target.value }))} placeholder="BASE" />
            </div>
            <div className="form-row">
              <label>{t('organization.name')}</label>
              <input value={payItemForm.name} onChange={(e) => setPayItemForm((f) => ({ ...f, name: e.target.value }))} placeholder="Base salary" />
            </div>
            <div className="form-row">
              <label>{t('organization.itemType')}</label>
              <select value={payItemForm.item_type} onChange={(e) => setPayItemForm((f) => ({ ...f, item_type: e.target.value }))}>
                <option value="EARNING">EARNING</option>
                <option value="DEDUCTION">DEDUCTION</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('organization.taxable')}</label>
              <select value={payItemForm.taxable ? 'true' : 'false'} onChange={(e) => setPayItemForm((f) => ({ ...f, taxable: e.target.value === 'true' }))}>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('organization.calculationType')}</label>
              <select value={payItemForm.calculation_type} onChange={(e) => setPayItemForm((f) => ({ ...f, calculation_type: e.target.value }))}>
                <option value="FIXED">FIXED</option>
                <option value="RATE">RATE</option>
                <option value="FORMULA">FORMULA</option>
              </select>
            </div>
            <div className="form-row">
              <label>{t('organization.defaultAmount')}</label>
              <input type="number" step={0.01} value={payItemForm.default_amount ?? ''} onChange={(e) => setPayItemForm((f) => ({ ...f, default_amount: e.target.value ? Number(e.target.value) : null }))} placeholder="0" />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowPayItemModal(false)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitPayItem}>{editingPayItem ? t('employees.save') : t('employees.addBtn')}</button>
            </div>
          </div>
        </div>
      )}

      {showChangePasswordModal && (
        <div className="modal-overlay" onClick={() => setShowChangePasswordModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('auth.changePassword')}</div>
            <div className="form-row">
              <label>{t('auth.currentPassword')}</label>
              <input type="password" value={changePasswordForm.current_password} onChange={(e) => setChangePasswordForm((f) => ({ ...f, current_password: e.target.value }))} />
            </div>
            <div className="form-row">
              <label>{t('auth.newPassword')}</label>
              <input type="password" value={changePasswordForm.new_password} onChange={(e) => setChangePasswordForm((f) => ({ ...f, new_password: e.target.value }))} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowChangePasswordModal(false)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitChangePassword}>{t('employees.save')}</button>
            </div>
          </div>
        </div>
      )}

      {showAddUserModal && (
        <div className="modal-overlay" onClick={() => setShowAddUserModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('auth.addUser')}</div>
            <div className="form-row">
              <label>{t('auth.username')}</label>
              <input value={addUserForm.username} onChange={(e) => setAddUserForm((f) => ({ ...f, username: e.target.value }))} placeholder="user1" />
            </div>
            <div className="form-row">
              <label>{t('auth.newPassword')}</label>
              <input type="password" value={addUserForm.password} onChange={(e) => setAddUserForm((f) => ({ ...f, password: e.target.value }))} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setShowAddUserModal(false)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitAddUser}>{t('employees.addBtn')}</button>
            </div>
          </div>
        </div>
      )}

      {resetPasswordUserId != null && (
        <div className="modal-overlay" onClick={() => setResetPasswordUserId(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">{t('auth.resetPassword')}</div>
            <div className="form-row">
              <label>{t('auth.newPassword')}</label>
              <input type="password" value={resetPasswordNew} onChange={(e) => setResetPasswordNew(e.target.value)} />
            </div>
            <div className="form-actions">
              <button type="button" className="btn-secondary" onClick={() => setResetPasswordUserId(null)}>{t('employees.cancel')}</button>
              <button type="button" className="primary-button" onClick={submitResetPassword}>{t('employees.save')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
