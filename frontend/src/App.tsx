import { useEffect, useState } from 'react'
import './App.css'

type Employee = {
  id: number
  emp_no: string
  first_name: string
  last_name: string
  email: string
  dept_id: number | null
  hire_date: string
  status: string
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

type TabKey = 'employees' | 'attendance' | 'payroll'

const API_BASE =
  import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL.length > 0
    ? import.meta.env.VITE_API_BASE_URL
    : 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>('employees')
  const [employees, setEmployees] = useState<Employee[]>([])
  const [attendance, setAttendance] = useState<AttendanceSummary[]>([])
  const [payRuns, setPayRuns] = useState<PayRun[]>([])
  const [selectedRun, setSelectedRun] = useState<number | null>(null)
  const [payResults, setPayResults] = useState<PayResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const currentYearMonth = new Date().toISOString().slice(0, 7).replace('-', '')

  async function fetchJson<T>(url: string): Promise<T> {
    const res = await fetch(url)
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`)
    }
    return (await res.json()) as T
  }

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true)
        setError(null)
        const [emp, att, runs] = await Promise.all([
          fetchJson<Employee[]>(`${API_BASE}/api/employees`),
          fetchJson<AttendanceSummary[]>(
            `${API_BASE}/api/attendance/monthly?year_month=${currentYearMonth}`,
          ),
          fetchJson<PayRun[]>(`${API_BASE}/api/payroll/runs`),
        ])
        setEmployees(emp)
        setAttendance(att)
        setPayRuns(runs)
        if (runs.length > 0) {
          setSelectedRun(runs[0].id)
          const results = await fetchJson<PayResult[]>(
            `${API_BASE}/api/payroll/runs/${runs[0].id}/results`,
          )
          setPayResults(results)
        }
      } catch (e) {
        setError('Failed to load data from JSCORP HR API.')
      } finally {
        setLoading(false)
      }
    }

    void bootstrap()
  }, [currentYearMonth])

  async function handleSelectRun(runId: number) {
    try {
      setSelectedRun(runId)
      setLoading(true)
      const results = await fetchJson<PayResult[]>(
        `${API_BASE}/api/payroll/runs/${runId}/results`,
      )
      setPayResults(results)
    } catch {
      setError('Failed to load payroll results.')
    } finally {
      setLoading(false)
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
              <div className="brand-text-main">JSCORP HR</div>
              <div className="brand-text-sub">People · Attendance · Payroll</div>
            </div>
          </div>
          <div className="app-badge">Mobile first</div>
        </header>

        <nav className="tab-nav" aria-label="Main modules">
          <button
            type="button"
            className={`tab-pill ${activeTab === 'employees' ? 'active' : ''}`}
            onClick={() => setActiveTab('employees')}
          >
            <span className="pill-dot" />
            Employees
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'attendance' ? 'active' : ''}`}
            onClick={() => setActiveTab('attendance')}
          >
            <span className="pill-dot" />
            Attendance
          </button>
          <button
            type="button"
            className={`tab-pill ${activeTab === 'payroll' ? 'active' : ''}`}
            onClick={() => setActiveTab('payroll')}
          >
            <span className="pill-dot" />
            Payroll
          </button>
        </nav>

        {loading && (
          <div className="section-subtitle" style={{ marginBottom: '0.6rem' }}>
            Loading latest JSCORP data…
          </div>
        )}
        {error && (
          <div className="section-subtitle" style={{ color: '#fecaca', marginBottom: '0.6rem' }}>
            {error}
          </div>
        )}

        {activeTab === 'employees' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">Employees overview</div>
                <div className="section-subtitle">JSCORP headcount snapshot</div>
              </div>
            </div>
            <div className="chip-row">
              <span className="chip soft">Active {activeEmpCount}</span>
              <span className="chip">Total {employees.length}</span>
            </div>
            <div className="list-card">
              <div className="list-header">
                <span>Employee</span>
                <span>Status</span>
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
                  <div className="list-value">
                    <span className={`badge-soft ${emp.status !== 'ACTIVE' ? 'warning' : ''}`}>
                      {emp.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="section-footer">
              <span>Tap an employee to manage details (future).</span>
              <button type="button" className="primary-button">
                Add employee
              </button>
            </div>
          </section>
        )}

        {activeTab === 'attendance' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">Monthly attendance</div>
                <div className="section-subtitle">
                  {currentYearMonth.slice(0, 4)}-{currentYearMonth.slice(4)} ·
                  JSCORP attendance summary
                </div>
              </div>
            </div>
            <div className="kpi-grid">
              <div className="kpi-card">
                <div className="kpi-label">Employees</div>
                <div className="kpi-main">{employees.length}</div>
                <div className="kpi-sub">Included in current month</div>
              </div>
              <div className="kpi-card">
                <div className="kpi-label">Tracked</div>
                <div className="kpi-main">{attendance.length}</div>
                <div className="kpi-sub">Attendance records</div>
              </div>
            </div>
            <div className="list-card">
              <div className="list-header">
                <span>Employee</span>
                <span>Hours · Issues</span>
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
                        Worked {row.worked_hours}h · Overtime {row.overtime_hours}h
                      </div>
                    </div>
                    <div className="list-value">
                      <span className={`badge-soft ${issues > 0 ? 'warning' : ''}`}>
                        {issues > 0 ? `${issues} issue(s)` : 'Clean'}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
            <div className="section-footer">
              <span>Aggregated from daily logs and leave records.</span>
              <button type="button" className="primary-button">
                Lock for payroll
              </button>
            </div>
          </section>
        )}

        {activeTab === 'payroll' && (
          <section>
            <div className="section-header">
              <div>
                <div className="section-title">Payroll runs</div>
                <div className="section-subtitle">Regular payroll for JSCORP employees</div>
              </div>
            </div>
            <div className="list-card" style={{ marginBottom: '0.7rem' }}>
              <div className="list-header">
                <span>Period</span>
                <span>Status</span>
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
                  <span>Employee</span>
                  <span>Net pay</span>
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
                          Gross {Number(res.gross_amount).toLocaleString()} · Deductions{' '}
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
              <span>Select a run to inspect net pay by employee.</span>
              <button type="button" className="primary-button">
                New payroll run
              </button>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

export default App
