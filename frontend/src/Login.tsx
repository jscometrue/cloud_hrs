import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import './App.css'

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${apiBase}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
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
      setError(err instanceof Error ? err.message : t('login.error'))
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
              style={{ color: '#fecaca', marginBottom: '0.75rem' }}
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
        </form>
      </div>
    </div>
  )
}
