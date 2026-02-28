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

## Environment variable (로그인 Not Found 해결)

로그인 시 "not found" 또는 "로그인 서버를 찾을 수 없습니다"가 나오면 **프론트엔드** 서비스에 아래 환경 변수를 넣고 **반드시 다시 배포**하세요.

- **Key**: `VITE_API_BASE_URL`
- **Value**: 백엔드 Public URL (끝에 슬래시 없이, 예: `https://jscorp-hr-backend.onrender.com`)

Vite는 빌드 시점에 이 값을 묶기 때문에, **환경 변수 추가/수정 후에는 "Manual Deploy" → "Clear build cache & deploy"로 한 번 더 배포**해야 적용됩니다.

백엔드 서비스 이름이 `*-backend.onrender.com` 형태면, 이 변수를 설정하지 않아도 앱이 자동으로 같은 호스트의 `-backend` 주소로 요청을 보내도록 되어 있습니다.

## "Made-with: Cursor" / 커밋 메시지로 인한 오류

Cursor가 커밋 메시지에 **Made-with: Cursor** 푸터를 붙이면, Render 배포나 웹훅에서 해당 문구가 포함된 긴 메시지로 인해 오류가 날 수 있습니다.

**해결 방법**
1. **Cursor 설정에서 비활성화**: Cursor → Settings → 검색에서 "commit" 또는 "Made with" → **Add 'Made with Cursor' to commits** 끄기.
2. **이미 푸시한 커밋 수정**:  
   `git commit --amend -m "fix: bcrypt 72-byte limit, CORS, login API URL override and Failed to fetch handling"`  
   (한 줄 메시지로만 작성, 따옴표 안에 원하는 메시지 입력 후)  
   `git push --force-with-lease origin main`  
   (주의: force push이므로 팀 작업 시 협의 후 진행)
