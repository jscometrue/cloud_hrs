# JSCORP HR Backend

FastAPI 기반 JSCORP 인사(근태 + 급여) 백엔드 API입니다.

## Requirements

- Python 3.11+

## Setup

```bash
cd backend
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

실행 후:

- 헬스체크: `http://localhost:8000/health`
- OpenAPI 문서: `http://localhost:8000/docs`

## Test

```bash
cd backend
pytest
```

