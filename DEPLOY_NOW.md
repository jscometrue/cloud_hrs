# 지금 배포하기 (Render.com)

아래 순서대로 하면 **몇 분 안에** 배포됩니다.

---

## 1. 저장소에 올리기

이 프로젝트를 **GitHub** 또는 **GitLab** 저장소에 푸시합니다.

```bash
cd c:\Cursor\HRS
git init
git add .
git commit -m "Deploy JSCORP HR"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

*(이미 저장소가 있으면 `git add .` → `git commit` → `git push` 만 하면 됩니다.)*

---

## 2. Render에서 배포

1. **https://dashboard.render.com** 접속 후 로그인
2. **New +** → **Blueprint** 선택
3. 저장소 연결: **Connect account**로 GitHub/GitLab 연결 후, 이 프로젝트 **저장소 선택**
4. Render가 **render.yaml**을 읽고 다음 두 서비스를 자동 생성합니다.
   - **jscorp-hr-backend** (Web Service)
   - **jscorp-hr-frontend** (Static Site)
5. **Apply** 또는 **Create resources** 클릭
6. 배포가 끝날 때까지 대기(보통 3~5분)

---

## 3. 배포 후 확인

- **백엔드 URL**: 서비스 목록에서 `jscorp-hr-backend` 클릭 → 상단 **URL** (예: `https://jscorp-hr-backend.onrender.com`)
- **프론트엔드 URL**: `jscorp-hr-frontend` URL (예: `https://jscorp-hr-frontend.onrender.com`)

프론트 URL로 접속한 뒤:

- 로그인 화면에서 **API 주소 설정**에 백엔드 URL 입력 (예: `https://jscorp-hr-backend.onrender.com`)
- **저장 후 새로고침** 후 로그인  
- 테스트 계정: **admin** / **admin123**

---

## 4. (선택) Render CLI로 배포

CLI가 설치되어 있으면 푸시 후 배포만 트리거할 수 있습니다.

```bash
render login
render deploys create
```

서비스는 이미 Blueprint로 만들어져 있어야 합니다.
