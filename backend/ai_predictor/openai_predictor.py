"""OpenAI GPT 모델 예측 클래스"""
import asyncio
import logging
from typing import Optional, Dict, Any
import openai
from openai import AsyncOpenAI

from config import settings

logger = logging.getLogger(__name__)


class OpenAIPredictor:
    """OpenAI GPT-5.2 모델을 사용한 주가 예측"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        """
        OpenAI Predictor 초기화
        
        Args:
            api_key: OpenAI API 키 (None이면 환경 변수에서 로드)
            timeout: API 호출 타임아웃 (초)
        """
        self.api_key = api_key or settings.openai_api_key
        self.timeout = timeout
        self.model = "gpt-4o-mini"  # 사용 가능한 모델로 변경
        
        if not self.api_key:
            logger.warning("OpenAI API 키가 설정되지 않았습니다. 이 모델은 건너뜁니다.")
            self.client = None
            return
        
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout)
        logger.info("OpenAI Predictor 초기화 완료")
    
    async def predict(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        주가 예측 수행
        
        Args:
            prompt: AI 모델에 전달할 프롬프트
            
        Returns:
            예측 결과 딕셔너리 (JSON 형식) 또는 None (API 키 없음)
            
        Raises:
            openai.APIError: API 호출 실패
            asyncio.TimeoutError: 타임아웃 발생
        """
        if not self.client:
            logger.warning("OpenAI 클라이언트가 초기화되지 않았습니다 (API 키 없음)")
            return None
        
        try:
            logger.info(f"OpenAI API 호출 시작 (모델: {self.model})")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 정확한 JSON 형식으로 주가를 예측해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI API 호출 성공")
            
            return {
                "model": self.model,
                "content": content,
                "success": True
            }
            
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI API 타임아웃: {e}")
            raise asyncio.TimeoutError(f"OpenAI API 타임아웃: {e}")
        
        except openai.APIError as e:
            logger.error(f"OpenAI API 오류: {e}")
            raise
        
        except Exception as e:
            logger.error(f"OpenAI 예측 중 예상치 못한 오류: {e}")
            raise
