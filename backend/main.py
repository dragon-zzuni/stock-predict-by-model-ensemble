# FastAPI 메인 애플리케이션
# 다중 AI 주식 예측 시스템 백엔드

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from config import settings

# 로깅 설정
def setup_logging():
    """로깅 설정 초기화"""
    # 로그 디렉토리 생성
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러
    file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 로깅 초기화
logger = setup_logging()

# FastAPI 앱 생성
app = FastAPI(
    title="다중 AI 주식 예측 시스템",
    description="5개의 AI 모델을 활용한 주식 가격 예측 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url, 
        "http://localhost:3000", 
        "http://localhost:3001",  # Vite 기본 포트
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 HTTP 요청을 로깅"""
    start_time = datetime.utcnow()
    
    # 요청 정보 로깅
    logger.info(f"요청 시작: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # 응답 시간 계산
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # 응답 정보 로깅
        logger.info(
            f"요청 완료: {request.method} {request.url.path} "
            f"- 상태: {response.status_code} - 소요 시간: {duration:.2f}초"
        )
        
        return response
        
    except Exception as e:
        # 미들웨어 레벨 오류
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"요청 실패: {request.method} {request.url.path} "
            f"- 오류: {str(e)} - 소요 시간: {duration:.2f}초",
            exc_info=True
        )
        raise

# 전역 예외 핸들러
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """요청 검증 오류 처리"""
    logger.error(f"요청 검증 실패: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "요청 데이터가 유효하지 않습니다",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "retryable": False
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 처리"""
    logger.error(f"예상치 못한 오류 발생: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
                "details": str(exc) if settings.log_level == "DEBUG" else None,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "retryable": True
            }
        }
    )

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("=" * 50)
    logger.info("다중 AI 주식 예측 시스템 시작")
    logger.info(f"환경 설정:")
    logger.info(f"  - Frontend URL: {settings.frontend_url}")
    logger.info(f"  - Ollama Host: {settings.ollama_host}")
    logger.info(f"  - Cache Enabled: {settings.cache_enabled}")
    logger.info(f"  - Log Level: {settings.log_level}")
    logger.info(f"  - AI Timeout: {settings.ai_timeout}초")
    logger.info("=" * 50)

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("다중 AI 주식 예측 시스템 종료")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "다중 AI 주식 예측 시스템 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    
    서버 상태 및 로컬 모델 로딩 상태 확인
    
    Returns:
        서버 상태 정보
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {}
    }
    
    # Ollama 로컬 모델 상태 확인
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ollama_host}/api/tags",
                timeout=2.0
            )
            if response.status_code == 200:
                models_data = response.json()
                models = [model.get("name", "") for model in models_data.get("models", [])]
                health_status["services"]["ollama"] = {
                    "status": "available",
                    "models": models
                }
            else:
                health_status["services"]["ollama"] = {
                    "status": "unavailable",
                    "reason": f"HTTP {response.status_code}"
                }
    except Exception as e:
        health_status["services"]["ollama"] = {
            "status": "unavailable",
            "reason": str(e)
        }
    
    # API 키 설정 확인 (키 값은 노출하지 않음)
    health_status["services"]["openai"] = {
        "configured": bool(settings.openai_api_key)
    }
    health_status["services"]["anthropic"] = {
        "configured": bool(settings.anthropic_api_key)
    }
    health_status["services"]["google"] = {
        "configured": bool(settings.google_api_key)
    }
    
    # 캐시 상태
    health_status["services"]["cache"] = {
        "enabled": settings.cache_enabled
    }
    
    return health_status

@app.get("/rankings")
async def get_rankings(force_refresh: bool = False):
    """
    거래대금 기준 상위 종목 조회
    
    Args:
        force_refresh: 강제 갱신 여부 (기본값: False)
        
    Returns:
        거래대금 상위 10개 종목 리스트
    """
    from services.ranking_service import ranking_service
    
    try:
        logger.info(f"거래대금 순위 조회 요청 (force_refresh={force_refresh})")
        rankings = await ranking_service.get_rankings(force_refresh=force_refresh)
        
        # Pydantic 모델을 dict로 변환
        rankings_dict = [ranking.dict() for ranking in rankings]
        
        return {
            "rankings": rankings_dict,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "count": len(rankings_dict)
        }
        
    except Exception as e:
        logger.error(f"거래대금 순위 조회 실패: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "RANKING_FETCH_FAILED",
                    "message": "거래대금 순위 데이터를 가져올 수 없습니다",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "retryable": True
                }
            }
        )


# 예측 요청 모델
class PredictRequest(BaseModel):
    """예측 요청 데이터 모델"""
    symbol: str = Field(..., description="종목 코드", example="005930.KS")
    market: str = Field(..., description="시장", example="KOSPI")
    company_name: str = Field("", description="회사명 (선택)", example="삼성전자")


@app.post("/predict")
async def predict_stock(request: PredictRequest):
    """
    주식 가격 예측
    
    Args:
        request: 예측 요청 (종목 코드, 시장, 회사명)
        
    Returns:
        예측 결과 (모델별 예측 + 종합 예측)
    """
    from services.prediction_service import prediction_service
    
    try:
        logger.info(f"예측 요청: {request.symbol} ({request.market})")
        
        # 예측 실행
        result = await prediction_service.predict(
            symbol=request.symbol,
            market=request.market,
            company_name=request.company_name
        )
        
        # 응답 생성
        response_data = {
            "symbol": result.symbol,
            "name": result.name,
            "current_price": result.current_price,
            "predictions": {},
            "ensemble": {},
            "timestamp": result.timestamp.isoformat() + "Z"
        }
        
        # 모델별 예측 변환
        for model_name, prediction in result.predictions.items():
            if prediction.success:
                response_data["predictions"][model_name] = {
                    period: {
                        "price": pred.price,
                        "reason": pred.reason,
                        "sentiment": pred.sentiment.value
                    }
                    for period, pred in prediction.predictions.items()
                }
        
        # 종합 예측 변환
        for period, ensemble_pred in result.ensemble.items():
            response_data["ensemble"][period] = {
                "price": ensemble_pred.price,
                "reason": ensemble_pred.reason,
                "sentiment": ensemble_pred.sentiment.value,
                "disagreement": ensemble_pred.disagreement,
                "std_dev": ensemble_pred.std_dev
            }
        
        logger.info(f"예측 완료: {request.symbol}")
        return response_data
        
    except ValueError as e:
        # 잘못된 입력
        logger.warning(f"잘못된 예측 요청: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "retryable": False
                }
            }
        )
    
    except RuntimeError as e:
        # 데이터 수집 실패 등
        logger.error(f"예측 실행 실패: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "PREDICTION_FAILED",
                    "message": "예측을 수행할 수 없습니다",
                    "details": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "retryable": True
                }
            }
        )
    
    except Exception as e:
        # 예상치 못한 오류
        logger.error(f"예측 중 오류 발생: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요",
                    "details": str(e) if settings.log_level == "DEBUG" else None,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "retryable": True
                }
            }
        )
