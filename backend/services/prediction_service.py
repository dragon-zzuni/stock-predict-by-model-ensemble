"""
예측 서비스 - 전체 예측 파이프라인 통합
"""
import time
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from config import settings
from data_collector.collector import DataCollector
from prompt_builder.builder import PromptBuilder
from ai_predictor.predictor import AIPredictor
from ai_predictor.parser import ResponseParser
from ensemble.engine import EnsembleEngine
from models.result import PredictionResult
from models.prediction import ModelPrediction


class PredictionService:
    """예측 파이프라인 통합 서비스"""
    
    def __init__(self):
        """초기화"""
        self.data_collector = DataCollector()
        self.prompt_builder = PromptBuilder()
        self.ai_predictor = AIPredictor(timeout=settings.ai_timeout)
        self.response_parser = ResponseParser()
        self.ensemble_engine = EnsembleEngine()
        
        logger.info("PredictionService 초기화 완료")
    
    async def predict(
        self, 
        symbol: str, 
        market: str, 
        company_name: str = ""
    ) -> PredictionResult:
        """
        주식 예측 전체 파이프라인 실행
        
        Args:
            symbol: 종목 코드
            market: 시장
            company_name: 회사명 (선택)
            
        Returns:
            PredictionResult: 예측 결과
            
        Raises:
            RuntimeError: 예측 실패
        """
        logger.info(f"예측 파이프라인 시작: {symbol} ({market})")
        start_time = time.time()
        
        try:
            # 1. 데이터 수집
            logger.info("1단계: 데이터 수집")
            collected_data = await self.data_collector.collect_all(
                symbol=symbol,
                market=market,
                company_name=company_name
            )
            
            # 2. 프롬프트 생성
            logger.info("2단계: 프롬프트 생성")
            prompts = self.prompt_builder.build_prompts_for_all_models(collected_data)
            
            # 3. AI 예측 실행
            logger.info("3단계: AI 모델 예측")
            raw_predictions = await self.ai_predictor.predict_all(prompts)
            
            # 4. 응답 파싱
            logger.info("4단계: 응답 파싱")
            parsed_predictions = self._parse_predictions(raw_predictions)
            
            # 5. 앙상블 계산
            logger.info("5단계: 앙상블 계산")
            ensemble_result = self.ensemble_engine.calculate_ensemble(parsed_predictions)
            
            # 6. 최종 결과 생성
            result = PredictionResult(
                symbol=symbol,
                name=company_name or symbol,
                current_price=collected_data.current_price,
                predictions=parsed_predictions,
                ensemble=ensemble_result,
                timestamp=datetime.utcnow()
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"예측 파이프라인 완료 (소요 시간: {elapsed_time:.2f}초)")
            
            return result
            
        except Exception as e:
            error_msg = f"예측 파이프라인 실패: {str(e)}"
            logger.error(error_msg)
            logger.exception(e)
            raise RuntimeError(f"예측 실패: {str(e)}")
    
    def _parse_predictions(
        self, 
        raw_predictions: Dict[str, Any]
    ) -> Dict[str, ModelPrediction]:
        """
        원시 AI 응답을 ModelPrediction 객체로 파싱
        
        Args:
            raw_predictions: 모델별 원시 응답
            
        Returns:
            파싱된 ModelPrediction 딕셔너리
        """
        parsed = {}
        
        for model_name, raw_response in raw_predictions.items():
            if raw_response is None:
                # 실패한 모델
                parsed[model_name] = ModelPrediction(
                    model_name=model_name,
                    predictions={},
                    timestamp=datetime.utcnow(),
                    success=False
                )
                continue
            
            try:
                # 응답 파싱
                parsed_prediction = self.response_parser.parse_response(model_name, raw_response)
                
                logger.info(f"{model_name} 파싱 결과: {parsed_prediction}")
                
                if parsed_prediction:
                    parsed[model_name] = parsed_prediction
                    logger.info(f"{model_name} 파싱 성공, predictions 추가 완료")
                else:
                    logger.warning(f"{model_name} 파싱 결과가 None입니다")
                    parsed[model_name] = ModelPrediction(
                        model_name=model_name,
                        predictions={},
                        timestamp=datetime.utcnow(),
                        success=False
                    )
                
            except Exception as e:
                logger.error(f"{model_name} 응답 파싱 실패: {e}", exc_info=True)
                parsed[model_name] = ModelPrediction(
                    model_name=model_name,
                    predictions={},
                    timestamp=datetime.utcnow(),
                    success=False
                )
        
        return parsed


# 전역 인스턴스
prediction_service = PredictionService()
