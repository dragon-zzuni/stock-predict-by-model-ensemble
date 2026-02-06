# 다중 AI 주식 예측 시스템

5개의 AI 모델(GPT-5.2, Gemini 3.0, Claude 4.5, Gemma, Qwen)을 활용한 앙상블 기반 주식 가격 예측 시스템입니다.

## 프로젝트 구조

```
.
├── backend/              # FastAPI 백엔드
│   ├── main.py          # FastAPI 애플리케이션
│   ├── config.py        # 설정 관리
│   ├── requirements.txt # Python 의존성
│   └── .env.example     # 환경 변수 예시
├── frontend/            # React 프론트엔드
│   ├── src/            # 소스 코드
│   ├── package.json    # Node.js 의존성
│   └── .env.example    # 환경 변수 예시
└── README.md           # 프로젝트 문서
```

## 시작하기

### 사전 요구사항

- Python 3.10 이상
- Node.js 18 이상
- Ollama (로컬 AI 모델 실행용)

### 백엔드 설정

1. 가상 환경 생성 및 활성화:
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:
```bash
copy .env.example .env
# .env 파일을 열어 API 키 등을 설정하세요
```

4. 서버 실행:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 설정

1. 의존성 설치:
```bash
cd frontend
npm install
```

2. 환경 변수 설정:
```bash
copy .env.example .env
# 필요시 .env 파일을 수정하세요
```

3. 개발 서버 실행:
```bash
npm run dev
```

프론트엔드는 http://localhost:3000 에서 실행됩니다.

## API 키 설정

다음 API 키가 필요합니다:

- **OpenAI API Key**: GPT-5.2 모델 사용
- **Anthropic API Key**: Claude 4.5 모델 사용
- **Google Cloud Credentials**: Gemini 3.0 모델 사용
- **News API Key**: 뉴스 데이터 수집 (선택사항)

로컬 모델(Gemma, Qwen)은 Ollama를 통해 실행되며 별도의 API 키가 필요하지 않습니다.

### Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (https://ollama.ai)
# 모델 다운로드
ollama pull gemma
ollama pull qwen
```

## 주요 기능

- 거래대금 기준 상위 종목 순위 조회
- 종목 검색 및 자동완성
- 5개 AI 모델의 병렬 예측 실행
- 앙상블 기반 종합 예측 제공
- 모델별 예측 근거 상세 보기
- 반응형 웹 디자인

## 기술 스택

### 백엔드
- FastAPI
- Python 3.10+
- Pydantic
- yfinance (주식 데이터)
- OpenAI, Anthropic, Google Cloud AI Platform (AI 모델)

### 프론트엔드
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (상태 관리)
- Axios (HTTP 클라이언트)

## 테스트

### 백엔드 테스트
```bash
cd backend
pytest
```

### 프론트엔드 테스트
```bash
cd frontend
npm test
```

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
