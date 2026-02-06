"""Ollama 로컬 모델 예측 클래스"""
import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
import json

from config import settings

logger = logging.getLogger(__name__)


class OllamaPredictor:
    """Ollama를 통한 로컬 모델(Gemma, Qwen) 주가 예측"""
    
    def __init__(self, host: Optional[str] = None, timeout: int = 10):
        """
        Ollama Predictor 초기화
        
        Args:
            host: Ollama 서버 주소 (None이면 환경 변수에서 로드)
            timeout: API 호출 타임아웃 (초)
        """
        self.host = host or settings.ollama_host
        self.timeout = timeout
        self.endpoint = f"{self.host}/api/generate"
        
        logger.info(f"Ollama Predictor 초기화 완료 (호스트: {self.host})")
    
    async def predict(self, prompt: str, model: str = "gemma") -> Dict[str, Any]:
        """
        주가 예측 수행
        
        Args:
            prompt: AI 모델에 전달할 프롬프트
            model: 사용할 모델 이름 ("gemma" 또는 "qwen")
            
        Returns:
            예측 결과 딕셔너리 (JSON 형식)
            
        Raises:
            aiohttp.ClientError: API 호출 실패
            asyncio.TimeoutError: 타임아웃 발생
        """
        try:
            logger.info(f"Ollama API 호출 시작 (모델: {model})")
            
            # 프롬프트에 JSON 형식 요청 추가
            enhanced_prompt = f"""{prompt}

응답은 반드시 다음과 같은 JSON 형식으로만 제공해주세요:
{{
  "1d": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1w": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}},
  "1m": {{"price": <숫자>, "reason": "<이유>", "sentiment": "긍정|부정"}}
}}"""
            
            payload = {
                "model": model,
                "prompt": enhanced_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            }
            
            timeout_obj = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.post(self.endpoint, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API 오류 (상태 코드: {response.status}): {error_text}")
                    
                    result = await response.json()
                    content = result.get("response", "")
                    
                    logger.info(f"Ollama API 호출 성공 (모델: {model})")
                    
                    return {
                        "model": model,
                        "content": content,
                        "success": True
                    }
        
        except asyncio.TimeoutError as e:
            logger.error(f"Ollama API 타임아웃 (모델: {model}): {e}")
            raise
        
        except aiohttp.ClientError as e:
            logger.error(f"Ollama API 연결 오류 (모델: {model}): {e}")
            raise
        
        except Exception as e:
            logger.error(f"Ollama 예측 중 오류 (모델: {model}): {e}")
            raise
    
    async def predict_gemma(self, prompt: str) -> Dict[str, Any]:
        """Gemma 모델로 예측"""
        return await self.predict(prompt, model="gemma3:1b")
    
    async def predict_qwen(self, prompt: str) -> Dict[str, Any]:
        """Qwen 모델로 예측"""
        return await self.predict(prompt, model="qwen3:8b")
