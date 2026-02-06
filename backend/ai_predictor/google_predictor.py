"""Google Gemini 모델 예측 클래스"""
import asyncio
import logging
from typing import Optional, Dict, Any
import json

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("google-generativeai 패키지가 설치되지 않았습니다")

from config import settings

logger = logging.getLogger(__name__)


class GooglePredictor:
    """Google Gemini 3.0 모델을 사용한 주가 예측"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        """
        Google Predictor 초기화
        
        Args:
            api_key: Google API 키 (None이면 환경 변수에서 로드)
            timeout: API 호출 타임아웃 (초)
        """
        if not GOOGLE_AI_AVAILABLE:
            logger.warning("google-generativeai 패키지가 설치되지 않았습니다. 이 모델은 건너뜁니다.")
            self.model = None
            return
        
        self.api_key = api_key or settings.google_api_key
        self.timeout = timeout
        self.model_name = "gemini-3-pro-preview"  # Gemini 3.0이 출시되면 변경
        
        if not self.api_key:
            logger.warning("Google API 키가 설정되지 않았습니다. 이 모델은 건너뜁니다.")
            self.model = None
            return
        
        # API 키 설정
        genai.configure(api_key=self.api_key)
        
        # 모델 초기화
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        logger.info("Google Predictor 초기화 완료")
    
    async def predict(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        주가 예측 수행
        
        Args:
            prompt: AI 모델에 전달할 프롬프트
            
        Returns:
            예측 결과 딕셔너리 (JSON 형식) 또는 None (API 키 없음)
            
        Raises:
            Exception: API 호출 실패
            asyncio.TimeoutError: 타임아웃 발생
        """
        if not self.model:
            logger.warning("Google 모델이 초기화되지 않았습니다 (API 키 없음)")
            return None
        
        try:
            logger.info(f"Google API 호출 시작 (모델: {self.model_name})")
            
            # 프롬프트에 JSON 형식 요청 추가
            enhanced_prompt = f"""{prompt}

분석적이고 논리적인 근거를 제시해주세요.
응답은 반드시 다음과 같은 JSON 형식으로만 제공해주세요:
{{
  "1d": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1w": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1m": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}}
}}"""
            
            # 비동기 실행을 위해 asyncio.to_thread 사용
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model.generate_content, enhanced_prompt),
                timeout=self.timeout
            )
            
            content = response.text
            logger.info("Google API 호출 성공")
            
            return {
                "model": self.model_name,
                "content": content,
                "success": True
            }
            
        except asyncio.TimeoutError as e:
            logger.error(f"Google API 타임아웃: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Google 예측 중 오류: {e}")
            raise
