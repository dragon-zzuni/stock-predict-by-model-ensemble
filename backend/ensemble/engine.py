"""
앙상블 엔진 - 다중 AI 모델 예측 통합
"""
import statistics
from typing import Dict, List, Optional
from collections import Counter
from models.prediction import ModelPrediction, PeriodPrediction, SentimentType
from models.result import EnsemblePrediction


class EnsembleEngine:
    """
    다중 AI 모델의 예측을 통합하여 종합 예측을 생성하는 앙상블 엔진
    
    주요 기능:
    - 기간별 예측 가격 평균 계산
    - 감성 다수결 투표
    - 표준편차 기반 의견 불일치 감지
    - 종합 예측 결과 생성
    """
    
    def __init__(self, disagreement_threshold: float = 0.2):
        """
        Args:
            disagreement_threshold: 의견 불일치 판단 기준 (표준편차/평균 비율)
        """
        self.disagreement_threshold = disagreement_threshold
    
    def calculate_ensemble(
        self, 
        predictions: Dict[str, ModelPrediction]
    ) -> Dict[str, EnsemblePrediction]:
        """
        여러 모델의 예측을 통합하여 종합 예측 계산
        
        Args:
            predictions: 모델명을 키로 하는 ModelPrediction 딕셔너리
            
        Returns:
            기간별 종합 예측 딕셔너리 {"1d": EnsemblePrediction, ...}
            
        Raises:
            ValueError: 유효한 예측이 없는 경우
        """
        if not predictions:
            raise ValueError("예측 데이터가 비어있습니다")
        
        # 성공한 예측만 필터링
        valid_predictions = {
            name: pred for name, pred in predictions.items() 
            if pred.success and pred.predictions
        }
        
        if not valid_predictions:
            raise ValueError("유효한 예측이 없습니다")
        
        ensemble = {}
        
        # 각 기간별로 종합 예측 계산
        for period in ["1d", "1w", "1m"]:
            ensemble_pred = self._calculate_period_ensemble(
                valid_predictions, 
                period
            )
            if ensemble_pred:
                ensemble[period] = ensemble_pred
        
        if not ensemble:
            raise ValueError("종합 예측을 생성할 수 없습니다")
        
        return ensemble
    
    def _calculate_period_ensemble(
        self,
        predictions: Dict[str, ModelPrediction],
        period: str
    ) -> Optional[EnsemblePrediction]:
        """
        특정 기간에 대한 종합 예측 계산
        
        Args:
            predictions: 유효한 모델 예측 딕셔너리
            period: 예측 기간 ("1d", "1w", "1m")
            
        Returns:
            해당 기간의 종합 예측 또는 None
        """
        # 해당 기간의 예측 수집
        period_predictions: List[PeriodPrediction] = []
        
        for model_pred in predictions.values():
            if period in model_pred.predictions:
                period_predictions.append(model_pred.predictions[period])
        
        if not period_predictions:
            return None
        
        # 가격 리스트 추출
        prices = [pred.price for pred in period_predictions]
        
        # 평균 가격 계산
        avg_price = sum(prices) / len(prices)
        
        # 표준편차 계산
        std_dev = statistics.stdev(prices) if len(prices) > 1 else 0.0
        
        # 의견 불일치 감지
        disagreement = (std_dev / avg_price) > self.disagreement_threshold if avg_price > 0 else False
        
        # 감성 다수결 투표
        sentiments = [pred.sentiment for pred in period_predictions]
        consensus_sentiment = self._vote_sentiment(sentiments)
        
        # 근거 통합 (모든 모델의 근거를 요약)
        reasons = [pred.reason for pred in period_predictions]
        combined_reason = self._combine_reasons(reasons)
        
        return EnsemblePrediction(
            price=round(avg_price, 2),
            reason=combined_reason,
            sentiment=consensus_sentiment,
            disagreement=disagreement,
            std_dev=round(std_dev, 2)
        )
    
    def _vote_sentiment(self, sentiments: List[SentimentType]) -> SentimentType:
        """
        감성 다수결 투표
        
        Args:
            sentiments: 감성 리스트
            
        Returns:
            가장 많은 표를 받은 감성
        """
        if not sentiments:
            return SentimentType.NEUTRAL
        
        sentiment_counts = Counter(sentiments)
        most_common = sentiment_counts.most_common(1)[0]
        return most_common[0]
    
    def _combine_reasons(self, reasons: List[str]) -> str:
        """
        여러 모델의 예측 근거를 통합
        
        Args:
            reasons: 근거 리스트
            
        Returns:
            통합된 근거 문자열
        """
        if not reasons:
            return "종합 분석 결과"
        
        # 중복 제거 및 요약
        unique_reasons = []
        seen = set()
        
        for reason in reasons:
            # 간단한 중복 체크 (정확한 매칭)
            if reason not in seen:
                unique_reasons.append(reason)
                seen.add(reason)
        
        # 최대 3개의 주요 근거만 포함
        if len(unique_reasons) > 3:
            combined = " | ".join(unique_reasons[:3]) + " 외"
        else:
            combined = " | ".join(unique_reasons)
        
        return combined
    
    def detect_disagreement(
        self, 
        predictions: Dict[str, ModelPrediction],
        period: str
    ) -> bool:
        """
        특정 기간에 대한 모델 간 의견 불일치 감지
        
        Args:
            predictions: 모델 예측 딕셔너리
            period: 예측 기간
            
        Returns:
            의견 불일치 여부
        """
        prices = []
        
        for model_pred in predictions.values():
            if model_pred.success and period in model_pred.predictions:
                prices.append(model_pred.predictions[period].price)
        
        if len(prices) < 2:
            return False
        
        avg_price = sum(prices) / len(prices)
        std_dev = statistics.stdev(prices)
        
        return (std_dev / avg_price) > self.disagreement_threshold if avg_price > 0 else False
    
    def calculate_consensus(
        self,
        predictions: Dict[str, ModelPrediction],
        period: str
    ) -> str:
        """
        특정 기간에 대한 감성 합의 계산
        
        Args:
            predictions: 모델 예측 딕셔너리
            period: 예측 기간
            
        Returns:
            합의된 감성 ("긍정", "부정", "중립")
        """
        sentiments = []
        
        for model_pred in predictions.values():
            if model_pred.success and period in model_pred.predictions:
                sentiments.append(model_pred.predictions[period].sentiment)
        
        if not sentiments:
            return SentimentType.NEUTRAL.value
        
        consensus = self._vote_sentiment(sentiments)
        return consensus.value
