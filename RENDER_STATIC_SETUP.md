# Render Static Site (Frontend) Setup

## Option A: With Root Directory (recommended)

| Field | Value |
|-------|--------|
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

## Option B: Without Root Directory (from repo root)

Use this if Root Directory is not set or not applied:

| Field | Value |
|-------|--------|
| **Root Directory** | *(leave blank)* |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

## Environment variable

- **Key**: `VITE_API_BASE_URL`
- **Value**: Your backend Public URL (e.g. `https://your-backend.onrender.com`)
