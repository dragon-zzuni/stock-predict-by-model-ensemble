"""AI 응답 파싱 모듈"""
import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

from models.prediction import PeriodPrediction, ModelPrediction

logger = logging.getLogger(__name__)


class ResponseParser:
    """AI 모델 응답 파싱 클래스"""
    
    @staticmethod
    def parse_response(
        model_name: str,
        response: Dict[str, Any]
    ) -> Optional[ModelPrediction]:
        """
        AI 모델 응답을 파싱하여 ModelPrediction 객체로 변환
        
        Args:
            model_name: 모델 이름
            response: AI 모델 응답 딕셔너리
        
        Returns:
            ModelPrediction 객체 또는 None (파싱 실패 시)
        """
        try:
            if not response or not response.get("success"):
                logger.warning(f"{model_name} 응답이 성공하지 않았습니다")
                return None
            
            content = response.get("content", "")
            if not content:
                logger.warning(f"{model_name} 응답 내용이 비어있습니다")
                return None
            
            logger.info(f"{model_name} 응답 내용 (처음 500자): {content[:500]}")
            
            # JSON 파싱
            parsed_data = ResponseParser._extract_json(content)
            if not parsed_data:
                logger.warning(f"{model_name} JSON 파싱 실패")
                logger.debug(f"{model_name} 전체 응답: {content}")
                return None
            
            logger.info(f"{model_name} JSON 파싱 성공: {parsed_data}")
            
            # 필수 필드 검증 및 추출
            predictions = {}
            for period in ["1d", "1w", "1m"]:
                period_data = parsed_data.get(period)
                if not period_data:
                    logger.warning(f"{model_name} {period} 데이터 없음")
                    continue
                
                logger.info(f"{model_name} {period} 데이터: {period_data}")
                
                # 필수 필드 추출
                price = period_data.get("price")
                reason = period_data.get("reason", "")
                sentiment = period_data.get("sentiment", "")
                
                logger.info(f"{model_name} {period} - price: {price}, reason: {reason[:50]}, sentiment: {sentiment}")
                
                # 가격 검증
                if price is None:
                    logger.warning(f"{model_name} {period} 가격 정보 없음")
                    continue
                
                try:
                    price = float(price)
                    logger.info(f"{model_name} {period} 가격 변환 성공: {price}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"{model_name} {period} 가격 형식 오류: {price}, 에러: {e}")
                    continue
                
                # 감성 정규화
                sentiment = ResponseParser._normalize_sentiment(sentiment)
                
                predictions[period] = PeriodPrediction(
                    price=price,
                    reason=reason,
                    sentiment=sentiment
                )
                logger.info(f"{model_name} {period} 예측 추가 완료")
            
            if not predictions:
                logger.warning(f"{model_name} 유효한 예측 데이터 없음")
                return None
            
            logger.info(f"{model_name} 총 {len(predictions)}개 기간 예측 생성 완료")
            
            return ModelPrediction(
                model_name=model_name,
                predictions=predictions,
                timestamp=datetime.now(),
                success=True
            )
        
        except Exception as e:
            logger.error(f"{model_name} 응답 파싱 중 오류: {e}")
            return None
    
    @staticmethod
    def _extract_json(content: str) -> Optional[Dict[str, Any]]:
        """
        텍스트에서 JSON 추출 및 파싱
        
        Args:
            content: AI 모델 응답 텍스트
        
        Returns:
            파싱된 JSON 딕셔너리 또는 None
        """
        try:
            # 직접 JSON 파싱 시도
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # JSON 코드 블록 추출 시도 (```json ... ```)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 중괄호로 둘러싸인 JSON 추출 시도
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning("JSON 추출 실패")
        return None
    
    @staticmethod
    def _normalize_sentiment(sentiment: str):
        """
        감성 값 정규화
        
        Args:
            sentiment: 원본 감성 값
        
        Returns:
            정규화된 감성 값 (SentimentType enum)
        """
        from models.prediction import SentimentType
        
        sentiment = sentiment.lower().strip()
        
        # 긍정 키워드
        positive_keywords = ["긍정", "positive", "bullish", "상승", "매수", "buy"]
        # 부정 키워드
        negative_keywords = ["부정", "negative", "bearish", "하락", "매도", "sell"]
        
        for keyword in positive_keywords:
            if keyword in sentiment:
                return SentimentType.POSITIVE
        
        for keyword in negative_keywords:
            if keyword in sentiment:
                return SentimentType.NEGATIVE
        
        # 기본값
        return SentimentType.NEUTRAL
    
    @staticmethod
    def parse_all_responses(
        responses: Dict[str, Optional[Dict[str, Any]]]
    ) -> Dict[str, Optional[ModelPrediction]]:
        """
        모든 AI 모델 응답을 파싱
        
        Args:
            responses: 모델별 응답 딕셔너리
        
        Returns:
            모델별 ModelPrediction 딕셔너리
        """
        parsed_predictions = {}
        
        for model_name, response in responses.items():
            if response is None:
                logger.warning(f"{model_name} 응답 없음")
                parsed_predictions[model_name] = None
                continue
            
            prediction = ResponseParser.parse_response(model_name, response)
            parsed_predictions[model_name] = prediction
            
            if prediction:
                logger.info(f"{model_name} 파싱 성공")
            else:
                logger.warning(f"{model_name} 파싱 실패")
        
        # 성공한 파싱 수 확인
        success_count = sum(1 for v in parsed_predictions.values() if v is not None)
        logger.info(f"응답 파싱 완료 (성공: {success_count}/{len(parsed_predictions)})")
        
        return parsed_predictions
