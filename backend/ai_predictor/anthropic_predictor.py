"""Anthropic Claude 모델 예측 클래스"""
import asyncio
import logging
from typing import Optional, Dict, Any

try:
    from anthropic import AsyncAnthropic, APIError, APITimeoutError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("anthropic 패키지가 설치되지 않았습니다")

from config import settings

logger = logging.getLogger(__name__)


class AnthropicPredictor:
    """Anthropic Claude 4.5 모델을 사용한 주가 예측"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        """
        Anthropic Predictor 초기화
        
        Args:
            api_key: Anthropic API 키 (None이면 환경 변수에서 로드)
            timeout: API 호출 타임아웃 (초)
        """
        if not ANTHROPIC_AVAILABLE:
            logger.warning("anthropic 패키지가 설치되지 않았습니다. 이 모델은 건너뜁니다.")
            self.client = None
            return
        
        self.api_key = api_key or settings.anthropic_api_key
        self.timeout = timeout
        self.model = "claude-3-5-sonnet-20241022"  # Claude 4.5가 출시되면 변경
        
        if not self.api_key:
            logger.warning("Anthropic API 키가 설정되지 않았습니다. 이 모델은 건너뜁니다.")
            self.client = None
            return
        
        self.client = AsyncAnthropic(api_key=self.api_key, timeout=self.timeout)
        logger.info("Anthropic Predictor 초기화 완료")
    
    async def predict(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        주가 예측 수행
        
        Args:
            prompt: AI 모델에 전달할 프롬프트
            
        Returns:
            예측 결과 딕셔너리 (JSON 형식) 또는 None (API 키 없음)
            
        Raises:
            APIError: API 호출 실패
            asyncio.TimeoutError: 타임아웃 발생
        """
        if not self.client:
            logger.warning("Anthropic 클라이언트가 초기화되지 않았습니다 (API 키 없음)")
            return None
        
        try:
            logger.info(f"Anthropic API 호출 시작 (모델: {self.model})")
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system="당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 정확한 JSON 형식으로 주가를 예측해주세요.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Claude는 content가 리스트 형태로 반환됨
            content = response.content[0].text if response.content else ""
            logger.info("Anthropic API 호출 성공")
            
            return {
                "model": self.model,
                "content": content,
                "success": True
            }
            
        except APITimeoutError as e:
            logger.error(f"Anthropic API 타임아웃: {e}")
            raise asyncio.TimeoutError(f"Anthropic API 타임아웃: {e}")
        
        except APIError as e:
            logger.error(f"Anthropic API 오류: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Anthropic 예측 중 예상치 못한 오류: {e}")
            raise
