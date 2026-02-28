import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import './App.css'

const API_BASE_KEY = 'jscorp_hr_api_base'

type Props = {
  apiBase: string
  onSuccess: (token: string) => void
}

export default function Login({ apiBase, onSuccess }: Props) {
  const { t } = useTranslation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [showApiSetting, setShowApiSetting] = useState(false)
  const [apiBaseInput, setApiBaseInput] = useState(apiBase)
  const [apiBaseSaved, setApiBaseSaved] = useState(false)
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'ok' | 'fail'>('idle')
  const [testMessage, setTestMessage] = useState<string>('')
  const [showForgotHint, setShowForgotHint] = useState(false)
  const [resetUsername, setResetUsername] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const [resetError, setResetError] = useState<string | null>(null)
  const [resetLink, setResetLink] = useState<string | null>(null)
  const effectiveApiBase = apiBase

  useEffect(() => {
    const url = `${apiBase}/health`
    const ctrl = new AbortController()
    const t = setTimeout(() => ctrl.abort(), 15000)
    fetch(url, { method: 'GET', mode: 'cors', signal: ctrl.signal })
      .then(() => clearTimeout(t))
      .catch(() => clearTimeout(t))
  }, [apiBase])

  async function testConnection() {
    const base = apiBaseInput.trim().replace(/\/$/, '')
    if (!base) {
      setTestStatus('fail')
      setTestMessage(t('login.testNoUrl'))
      return
    }
    setTestStatus('testing')
    setTestMessage('')
    const url = `${base}/health`
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 25000)
    try {
      const res = await fetch(url, { method: 'GET', mode: 'cors', signal: controller.signal })
      clearTimeout(timeoutId)
      if (res.ok) {
        setTestStatus('ok')
        setTestMessage(t('login.testOk'))
      } else {
        setTestStatus('fail')
        setTestMessage(t('login.testFail') + ` (${res.status})`)
      }
    } catch (e) {
      clearTimeout(timeoutId)
      setTestStatus('fail')
      const msg = e instanceof Error ? e.message : String(e)
      setTestMessage(t('login.testFail') + ': ' + (msg === 'Failed to fetch' ? t('login.testFailNetwork') : msg))
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    const u = (username || '').trim()
    const p = password ?? ''
    if (!u) {
      setError(t('login.error'))
      return
    }
    setLoading(true)
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 70000)
      const res = await fetch(`${effectiveApiBase}/api/auth/login`, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p }),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      const data = await res.json().catch(() => ({})) as { detail?: string; access_token?: string }
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error(t('login.notFound'))
        }
        if (res.status === 403) {
          throw new Error(t('login.verifyEmailFirst'))
        }
        throw new Error(data.detail || 'Login failed')
      }
      const token = data.access_token
      if (!token || typeof token !== 'string') {
        throw new Error(t('login.error'))
      }
      onSuccess(token)
    } catch (err) {
      const msg = err instanceof Error ? err.message : ''
      const isNetwork = msg === 'Failed to fetch' || msg.includes('fetch') || (err instanceof Error && err.name === 'AbortError')
      if (isNetwork) {
        setError(t('login.failedToFetch'))
      } else {
        setError(msg || t('login.error'))
      }
    } finally {
      setLoading(false)
    }
  }

  async function handleRequestPasswordReset() {
    const user = (resetUsername || username).trim()
    setResetError(null)
    setResetLink(null)
    if (!user) {
      setResetError(t('login.notFound'))
      return
    }
    setResetLoading(true)
    try {
      const res = await fetch(`${effectiveApiBase}/api/auth/request-password-reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error((data as { detail?: string }).detail || 'Failed')
      }
      const token = (data as { token?: string }).token
      if (token) {
        const url = `${window.location.origin}${window.location.pathname}?reset=${token}`
        setResetLink(url)
      }
    } catch (e) {
      setResetError(e instanceof Error ? e.message : 'Failed')
    } finally {
      setResetLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <div className="card-surface" style={{ maxWidth: '400px', margin: '2rem auto' }}>
        <header className="app-header" style={{ marginBottom: '1.5rem' }}>
          <div className="app-brand">
            <div className="brand-badge">JS</div>
            <div>
              <div className="brand-text-main">{t('app.title')}</div>
              <div className="brand-text-sub">{t('app.subtitle')}</div>
            </div>
          </div>
        </header>
        <form onSubmit={handleSubmit}>
          <div className="modal-title" style={{ marginBottom: '1rem' }}>
            {t('login.title')}
          </div>
          {error && (
            <div style={{ marginBottom: '0.75rem' }}>
              <div
                className="section-subtitle"
                style={{ color: '#fecaca', wordBreak: 'break-all' }}
              >
                {error}
              </div>
              {error === t('login.failedToFetch') && (
                <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                  <p>{t('login.failedToFetchHint')}</p>
                  <a
                    href={effectiveApiBase}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ display: 'inline-block', marginTop: '0.5rem', color: 'var(--primary, #60a5fa)' }}
                  >
                    {t('login.openBackendUrl')}
                  </a>
                </div>
              )}
            </div>
          )}
          <div className="form-row">
            <label>{t('login.username')}</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={t('login.placeholderUsername')}
              autoComplete="username"
              required
            />
          </div>
          <div className="form-row">
            <label>{t('login.password')}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('login.placeholderPassword')}
              autoComplete="current-password"
              required
            />
            <button
              type="button"
              className="btn-secondary"
              style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}
              onClick={() => setShowForgotHint(!showForgotHint)}
            >
              {t('login.forgotPassword')}
            </button>
            {showForgotHint && (
              <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                <p>{t('login.forgotPasswordHint')}</p>
                <div className="form-row" style={{ marginTop: '0.5rem' }}>
                  <label style={{ fontSize: '0.75rem' }}>{t('login.username')}</label>
                  <input
                    type="text"
                    value={resetUsername}
                    onChange={(e) => setResetUsername(e.target.value)}
                    placeholder={t('login.placeholderUsername')}
                  />
                </div>
                <button
                  type="button"
                  className="btn-secondary"
                  style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}
                  onClick={handleRequestPasswordReset}
                  disabled={resetLoading}
                >
                  {t('login.requestPasswordReset')}
                </button>
                {resetError && (
                  <p style={{ color: '#fecaca', marginTop: '0.25rem' }}>{resetError}</p>
                )}
                {resetLink && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <p>{t('login.resetRequested')}</p>
                    <a
                      href={resetLink}
                      style={{ color: 'var(--primary, #60a5fa)' }}
                    >
                      {resetLink}
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="form-actions" style={{ marginTop: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? t('login.loggingIn') : t('login.submit')}
            </button>
            {error && (
              <button
                type="button"
                className="btn-secondary"
                onClick={() => { setError(null); setLoading(false) }}
              >
                {t('login.retry')}
              </button>
            )}
          </div>
          <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border, #374151)' }}>
            <button
              type="button"
              className="btn-secondary"
              style={{ fontSize: '0.8rem' }}
              onClick={() => { setShowApiSetting(!showApiSetting); setApiBaseInput(apiBase); setApiBaseSaved(false) }}
            >
              {t('login.apiSetting')}
            </button>
            {showApiSetting && (
              <div style={{ marginTop: '0.75rem' }}>
                <label style={{ display: 'block', fontSize: '0.8rem', marginBottom: '0.25rem' }}>{t('login.apiBaseUrl')}</label>
                <input
                  type="url"
                  value={apiBaseInput}
                  onChange={(e) => { setApiBaseInput(e.target.value); setTestStatus('idle') }}
                  placeholder="https://jscorp-hr-backend.onrender.com"
                  style={{ width: '100%', padding: '0.4rem', fontSize: '0.85rem', marginBottom: '0.5rem' }}
                />
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
                  <button
                    type="button"
                    className="btn-secondary"
                    style={{ fontSize: '0.8rem' }}
                    onClick={testConnection}
                    disabled={testStatus === 'testing'}
                  >
                    {testStatus === 'testing' ? t('login.testing') : t('login.testConnection')}
                  </button>
                  {testStatus === 'ok' && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--success, #34d399)' }}>{testMessage}</span>
                  )}
                  {testStatus === 'fail' && (
                    <span style={{ fontSize: '0.8rem', color: '#fecaca' }}>{testMessage}</span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <button
                    type="button"
                    className="primary-button"
                    style={{ fontSize: '0.8rem' }}
                    onClick={() => {
                      const v = apiBaseInput.trim().replace(/\/$/, '')
                      if (v) {
                        localStorage.setItem(API_BASE_KEY, v)
                        setApiBaseSaved(true)
                        setTimeout(() => window.location.reload(), 600)
                      }
                    }}
                  >
                    {t('login.saveAndReload')}
                  </button>
                  {apiBaseSaved && <span style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{t('login.reloading')}</span>}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>{t('login.apiSettingHint')}</p>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
