import { useState } from 'react'
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
  const effectiveApiBase = apiBase

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 70000)
      const res = await fetch(`${effectiveApiBase}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error(t('login.notFound'))
        }
        const data = await res.json().catch(() => ({}))
        throw new Error((data as { detail?: string }).detail || 'Login failed')
      }
      const data = (await res.json()) as { access_token: string }
      onSuccess(data.access_token)
    } catch (err) {
      const msg = err instanceof Error ? err.message : ''
      const isNetwork = msg === 'Failed to fetch' || msg.includes('fetch') || (err instanceof Error && err.name === 'AbortError')
      if (isNetwork) {
        setError(t('login.failedToFetch') + ' (URL: ' + effectiveApiBase + ')')
      } else {
        setError(msg || t('login.error'))
      }
    } finally {
      setLoading(false)
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
            <div
              className="section-subtitle"
              style={{ color: '#fecaca', marginBottom: '0.75rem', wordBreak: 'break-all' }}
            >
              {error}
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
          </div>
          <div className="form-actions" style={{ marginTop: '1.25rem' }}>
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? t('login.loggingIn') : t('login.submit')}
            </button>
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
                  onChange={(e) => setApiBaseInput(e.target.value)}
                  placeholder="https://jscorp-hr-backend.onrender.com"
                  style={{ width: '100%', padding: '0.4rem', fontSize: '0.85rem', marginBottom: '0.5rem' }}
                />
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
