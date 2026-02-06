# 환경 변수 및 설정 관리
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 키
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None  # Google AI Studio API 키
    news_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None  # Alpha Vantage API 키 (선택)
    
    # Ollama 설정
    ollama_host: str = "http://localhost:11434"
    
    # 캐시 설정
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 86400
    cache_enabled: bool = True
    
    # AWS 설정
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_region: str = "ap-northeast-2"
    
    # 서버 설정
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # AI 모델 설정
    ai_timeout: int = 120  # CPU 환경의 Ollama를 위해 기본값 120초
    ai_max_retries: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()
