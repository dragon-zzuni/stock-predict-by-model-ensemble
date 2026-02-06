"""AI 예측 통합 클래스"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ai_predictor.openai_predictor import OpenAIPredictor
from ai_predictor.google_predictor import GooglePredictor
from ai_predictor.anthropic_predictor import AnthropicPredictor
from ai_predictor.ollama_predictor import OllamaPredictor
from config import settings

logger = logging.getLogger(__name__)


class AIPredictor:
    """다중 AI 모델 통합 예측 클래스"""
    
    def __init__(self, timeout: int = 10):
        """
        AI Predictor 초기화
        
        Args:
            timeout: 각 모델 호출 타임아웃 (초)
        """
        self.timeout = timeout
        self.predictors = {}
        
        # 각 예측기 초기화 (실패해도 계속 진행)
        self._init_predictors()
        
        logger.info(f"AI Predictor 초기화 완료 (활성 모델: {len(self.predictors)}개)")
    
    def _init_predictors(self):
        """개별 예측기 초기화"""
        # OpenAI
        try:
            predictor = OpenAIPredictor(timeout=self.timeout)
            if predictor.client:  # API 키가 있고 초기화 성공한 경우만 추가
                self.predictors["GPT"] = predictor
                logger.info("OpenAI 예측기 초기화 성공")
        except Exception as e:
            logger.warning(f"OpenAI 예측기 초기화 실패: {e}")
        
        # Google
        try:
            predictor = GooglePredictor(timeout=self.timeout)
            if predictor.model:  # API 키가 있고 초기화 성공한 경우만 추가
                self.predictors["Gemini"] = predictor
                logger.info("Google 예측기 초기화 성공")
        except Exception as e:
            logger.warning(f"Google 예측기 초기화 실패: {e}")
        
        # Anthropic
        try:
            predictor = AnthropicPredictor(timeout=self.timeout)
            if predictor.client:  # API 키가 있고 초기화 성공한 경우만 추가
                self.predictors["Claude"] = predictor
                logger.info("Anthropic 예측기 초기화 성공")
        except Exception as e:
            logger.warning(f"Anthropic 예측기 초기화 실패: {e}")
        
        # Ollama (로컬 모델 - 항상 시도)
        try:
            self.predictors["Ollama"] = OllamaPredictor(timeout=self.timeout)
            logger.info("Ollama 예측기 초기화 성공")
        except Exception as e:
            logger.warning(f"Ollama 예측기 초기화 실패: {e}")
    
    async def predict_all(self, prompts: Dict[str, str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        모든 AI 모델에 병렬로 예측 요청
        
        Args:
            prompts: 모델별 프롬프트 딕셔너리
                    {"gpt": "...", "gemini": "...", "claude": "...", "gemma": "...", "qwen": "..."}
        
        Returns:
            모델별 예측 결과 딕셔너리
            {"GPT-5.2": {...}, "Gemini 3.0": {...}, ...}
        """
        logger.info("다중 AI 모델 예측 시작")
        
        tasks = []
        model_names = []
        
        # GPT
        if "GPT" in self.predictors and "gpt" in prompts:
            tasks.append(self._safe_predict("GPT-5.2", self.predictors["GPT"].predict, prompts["gpt"]))
            model_names.append("GPT-5.2")
        
        # Gemini
        if "Gemini" in self.predictors and "gemini" in prompts:
            tasks.append(self._safe_predict("Gemini 3.0", self.predictors["Gemini"].predict, prompts["gemini"]))
            model_names.append("Gemini 3.0")
        
        # Claude
        if "Claude" in self.predictors and "claude" in prompts:
            tasks.append(self._safe_predict("Claude 4.5", self.predictors["Claude"].predict, prompts["claude"]))
            model_names.append("Claude 4.5")
        
        # Gemma (Ollama)
        if "Ollama" in self.predictors and "gemma" in prompts:
            tasks.append(self._safe_predict("Gemma", self.predictors["Ollama"].predict_gemma, prompts["gemma"]))
            model_names.append("Gemma")
        
        # Qwen (Ollama)
        if "Ollama" in self.predictors and "qwen" in prompts:
            tasks.append(self._safe_predict("Qwen", self.predictors["Ollama"].predict_qwen, prompts["qwen"]))
            model_names.append("Qwen")
        
        if not tasks:
            logger.error("사용 가능한 AI 모델이 없습니다")
            return {}
        
        # 병렬 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        predictions = {}
        for model_name, result in zip(model_names, results):
            if isinstance(result, Exception):
                logger.error(f"{model_name} 예측 실패: {result}")
                predictions[model_name] = None
            elif result is None:
                logger.warning(f"{model_name} 예측 결과 없음")
                predictions[model_name] = None
            else:
                predictions[model_name] = result
                logger.info(f"{model_name} 예측 성공")
        
        # 성공한 모델 수 확인
        success_count = sum(1 for v in predictions.values() if v is not None)
        logger.info(f"다중 AI 모델 예측 완료 (성공: {success_count}/{len(predictions)})")
        
        if success_count == 0:
            logger.error("모든 AI 모델 예측 실패")
        
        return predictions
    
    async def _safe_predict(
        self, 
        name: str, 
        predict_fn, 
        prompt: str
    ) -> Optional[Dict[str, Any]]:
        """
        타임아웃과 예외 처리를 포함한 안전한 예측
        
        Args:
            name: 모델 이름
            predict_fn: 예측 함수
            prompt: 프롬프트
        
        Returns:
            예측 결과 또는 None
        """
        try:
            result = await asyncio.wait_for(
                predict_fn(prompt),
                timeout=self.timeout
            )
            return result
        
        except asyncio.TimeoutError:
            logger.warning(f"{name} 모델 타임아웃 ({self.timeout}초)")
            return None
        
        except Exception as e:
            logger.error(f"{name} 모델 오류: {e}")
            return None
