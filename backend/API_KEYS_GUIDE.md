# API 키 발급 가이드

## 📋 API 키 필요 여부 요약

| API | 필요 여부 | 용도 | 무료 플랜 |
|-----|----------|------|----------|
| **FinanceDataReader** | ❌ 불필요 | 한국 주식 데이터 | ✅ 완전 무료 |
| **PyKrx** | ❌ 불필요 | 한국거래소 데이터 | ✅ 완전 무료 |
| **Yahoo Finance** | ❌ 불필요 | 글로벌 주식 데이터 | ✅ 무료 (Rate limit 있음) |
| **NewsAPI** | ✅ 필요 | 뉴스 데이터 | ✅ 무료 (제한적) |
| **Alpha Vantage** | ✅ 필요 (선택) | 미국 주식 데이터 | ✅ 무료 (500 calls/day) |
| **OpenAI** | ✅ 필요 (선택) | GPT 모델 | ❌ 유료 |
| **Anthropic** | ✅ 필요 (선택) | Claude 모델 | ❌ 유료 |
| **Google** | ✅ 필요 (선택) | Gemini 모델 | ✅ 무료 tier 있음 |

---

## 1. NewsAPI (뉴스 데이터) ⭐ 권장

### 발급 방법
1. https://newsapi.org/ 접속
2. "Get API Key" 클릭
3. 이메일로 회원가입
4. API 키 자동 발급

### 무료 플랜 제한
- ✅ `/v2/top-headlines` 사용 가능
- ❌ `/v2/everything` 사용 불가 (Business 플랜 필요)
- 100 requests/day

### .env 설정
```bash
NEWS_API_KEY=your_newsapi_key_here
```

---

## 2. Alpha Vantage (미국 주식 데이터) - 선택사항

### 발급 방법
1. https://www.alphavantage.co/support/#api-key 접속
2. 이메일 입력
3. API 키 즉시 발급

### 무료 플랜 제한
- 500 API calls/day
- 5 API calls/minute

### .env 설정
```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
```

### 참고
- Alpha Vantage는 **선택사항**입니다
- 설정하지 않아도 Yahoo Finance, FinanceDataReader, PyKrx로 작동
- 미국 주식 데이터 보강용

---

## 3. OpenAI (GPT 모델) - 선택사항

### 발급 방법
1. https://platform.openai.com/ 접속
2. 회원가입 및 로그인
3. "API Keys" 메뉴에서 "Create new secret key" 클릭
4. API 키 복사 (한 번만 표시됨!)

### 요금
- 유료 (사용량 기반)
- GPT-4: $0.03/1K tokens (input)
- 신규 가입 시 $5 크레딧 제공

### .env 설정
```bash
OPENAI_API_KEY=sk-...your_key_here
```

---

## 4. Anthropic (Claude 모델) - 선택사항

### 발급 방법
1. https://console.anthropic.com/ 접속
2. 회원가입 및 로그인
3. "API Keys" 메뉴에서 키 생성
4. API 키 복사

### 요금
- 유료 (사용량 기반)
- Claude 3.5: $3/MTok (input)
- 신규 가입 시 $5 크레딧 제공

### .env 설정
```bash
ANTHROPIC_API_KEY=sk-ant-...your_key_here
```

---

## 5. Google AI Studio (Gemini 모델) - 선택사항

### 발급 방법
1. https://makersuite.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. API 키 복사

### 무료 플랜
- ✅ 60 requests/minute
- ✅ 무료 tier 제공

### .env 설정
```bash
GOOGLE_API_KEY=AIza...your_key_here
```

---

## 🚀 최소 설정으로 시작하기

### 필수 설정 (무료)
```bash
# 뉴스 데이터용 (무료)
NEWS_API_KEY=your_newsapi_key_here

# Ollama 로컬 모델 (무료)
OLLAMA_HOST=http://localhost:11434
```

### 권장 설정 (무료 + 선택)
```bash
# 뉴스 데이터
NEWS_API_KEY=your_newsapi_key_here

# 미국 주식 보강 (선택)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Google Gemini (무료 tier)
GOOGLE_API_KEY=your_google_api_key_here

# Ollama 로컬
OLLAMA_HOST=http://localhost:11434
```

---

## 📝 .env 파일 설정 예시

```bash
# ===== 필수 설정 =====
NEWS_API_KEY=abc123...

# ===== 선택 설정 (주식 데이터) =====
ALPHA_VANTAGE_API_KEY=xyz789...

# ===== 선택 설정 (AI 모델) =====
GOOGLE_API_KEY=AIza...
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# ===== 로컬 모델 =====
OLLAMA_HOST=http://localhost:11434

# ===== 서버 설정 =====
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=INFO
AI_TIMEOUT=10
CACHE_ENABLED=true
```

---

## ❓ FAQ

### Q: API 키 없이 사용할 수 있나요?
**A:** 네! 다음 기능은 API 키 없이 사용 가능합니다:
- ✅ 주식 데이터 수집 (FinanceDataReader, PyKrx, Yahoo Finance)
- ✅ 로컬 AI 모델 (Ollama - Gemma, Qwen)
- ❌ 뉴스 데이터 (NewsAPI 키 필요)
- ❌ 외부 AI 모델 (OpenAI, Anthropic, Google 키 필요)

### Q: 어떤 API 키를 먼저 발급받아야 하나요?
**A:** 우선순위:
1. **NewsAPI** (무료, 뉴스 감성 분석용)
2. **Google AI Studio** (무료 tier, Gemini 모델)
3. Alpha Vantage (선택, 미국 주식 보강)

### Q: 유료 API를 사용하지 않으면 어떻게 되나요?
**A:** 
- 주식 데이터는 정상 작동 (무료 소스 사용)
- AI 예측은 Ollama 로컬 모델만 사용
- 뉴스 데이터는 더미 데이터 반환

### Q: Rate Limit에 걸리면 어떻게 되나요?
**A:** 
- Fallback 시스템이 자동으로 다른 데이터 소스로 전환
- 모든 소스 실패 시 Mock 데이터 반환
- 시스템은 계속 작동

---

## 🔒 보안 주의사항

1. **절대 API 키를 코드에 하드코딩하지 마세요**
2. **.env 파일을 Git에 커밋하지 마세요** (.gitignore에 포함됨)
3. **API 키를 공개 저장소에 업로드하지 마세요**
4. **정기적으로 API 키를 갱신하세요**

---

## 📞 문의

API 키 발급 중 문제가 발생하면:
1. 각 서비스의 공식 문서 확인
2. 이메일 인증 확인
3. 무료 tier 제한 확인
