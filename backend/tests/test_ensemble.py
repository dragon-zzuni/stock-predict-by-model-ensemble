"""
앙상블 엔진 테스트
"""
import pytest
from datetime import datetime
from backend.ensemble import EnsembleEngine
from backend.models.prediction import ModelPrediction, PeriodPrediction, SentimentType


class TestEnsembleEngine:
    """EnsembleEngine 클래스 테스트"""
    
    def test_calculate_ensemble_basic(self):
        """기본 앙상블 계산 테스트"""
        engine = EnsembleEngine()
        
        # 테스트 데이터 생성
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승 예상", sentiment=SentimentType.POSITIVE),
                    "1w": PeriodPrediction(price=110.0, reason="긍정적", sentiment=SentimentType.POSITIVE),
                    "1m": PeriodPrediction(price=120.0, reason="장기 상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=110.0, reason="강세", sentiment=SentimentType.POSITIVE),
                    "1w": PeriodPrediction(price=105.0, reason="보합", sentiment=SentimentType.NEUTRAL),
                    "1m": PeriodPrediction(price=90.0, reason="하락 우려", sentiment=SentimentType.NEGATIVE)
                },
                success=True
            ),
            "model3": ModelPrediction(
                model_name="model3",
                predictions={
                    "1d": PeriodPrediction(price=90.0, reason="하락", sentiment=SentimentType.NEGATIVE),
                    "1w": PeriodPrediction(price=115.0, reason="회복", sentiment=SentimentType.POSITIVE),
                    "1m": PeriodPrediction(price=130.0, reason="강세", sentiment=SentimentType.POSITIVE)
                },
                success=True
            )
        }
        
        # 앙상블 계산
        ensemble = engine.calculate_ensemble(predictions)
        
        # 검증
        assert "1d" in ensemble
        assert "1w" in ensemble
        assert "1m" in ensemble
        
        # 1일 후 평균: (100 + 110 + 90) / 3 = 100
        assert ensemble["1d"].price == 100.0
        
        # 1주일 후 평균: (110 + 105 + 115) / 3 = 110
        assert ensemble["1w"].price == 110.0
        
        # 1개월 후 평균: (120 + 90 + 130) / 3 = 113.33
        assert abs(ensemble["1m"].price - 113.33) < 0.01
    
    def test_sentiment_voting(self):
        """감성 다수결 투표 테스트"""
        engine = EnsembleEngine()
        
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=110.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model3": ModelPrediction(
                model_name="model3",
                predictions={
                    "1d": PeriodPrediction(price=90.0, reason="하락", sentiment=SentimentType.NEGATIVE)
                },
                success=True
            )
        }
        
        ensemble = engine.calculate_ensemble(predictions)
        
        # 긍정 2표, 부정 1표 -> 긍정이 다수
        assert ensemble["1d"].sentiment == SentimentType.POSITIVE
    
    def test_disagreement_detection(self):
        """의견 불일치 감지 테스트"""
        engine = EnsembleEngine(disagreement_threshold=0.2)
        
        # 의견 불일치가 있는 경우 (표준편차가 큼)
        predictions_disagree = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=150.0, reason="강세", sentiment=SentimentType.POSITIVE)
                },
                success=True
            )
        }
        
        ensemble = engine.calculate_ensemble(predictions_disagree)
        
        # 평균 125, 표준편차 약 35.36, 35.36/125 = 0.283 > 0.2
        assert ensemble["1d"].disagreement is True
        
        # 의견 일치가 있는 경우 (표준편차가 작음)
        predictions_agree = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=105.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            )
        }
        
        ensemble = engine.calculate_ensemble(predictions_agree)
        
        # 평균 102.5, 표준편차 약 3.54, 3.54/102.5 = 0.034 < 0.2
        assert ensemble["1d"].disagreement is False
    
    def test_partial_failure_handling(self):
        """일부 모델 실패 시 처리 테스트"""
        engine = EnsembleEngine()
        
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=1.0, reason="실패", sentiment=SentimentType.NEUTRAL)
                },
                success=False  # 실패한 모델
            ),
            "model3": ModelPrediction(
                model_name="model3",
                predictions={
                    "1d": PeriodPrediction(price=110.0, reason="강세", sentiment=SentimentType.POSITIVE)
                },
                success=True
            )
        }
        
        # 실패한 모델을 제외하고 앙상블 계산
        ensemble = engine.calculate_ensemble(predictions)
        
        # 성공한 2개 모델의 평균: (100 + 110) / 2 = 105
        assert ensemble["1d"].price == 105.0
    
    def test_empty_predictions_error(self):
        """빈 예측 데이터 오류 테스트"""
        engine = EnsembleEngine()
        
        with pytest.raises(ValueError, match="예측 데이터가 비어있습니다"):
            engine.calculate_ensemble({})
    
    def test_all_failed_predictions_error(self):
        """모든 예측 실패 시 오류 테스트"""
        engine = EnsembleEngine()
        
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=1.0, reason="실패", sentiment=SentimentType.NEUTRAL)
                },
                success=False
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=1.0, reason="실패", sentiment=SentimentType.NEUTRAL)
                },
                success=False
            )
        }
        
        with pytest.raises(ValueError, match="유효한 예측이 없습니다"):
            engine.calculate_ensemble(predictions)
    
    def test_detect_disagreement_method(self):
        """detect_disagreement 메서드 테스트"""
        engine = EnsembleEngine(disagreement_threshold=0.2)
        
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=150.0, reason="강세", sentiment=SentimentType.POSITIVE)
                },
                success=True
            )
        }
        
        # 의견 불일치 감지
        assert engine.detect_disagreement(predictions, "1d") is True
        
        # 존재하지 않는 기간
        assert engine.detect_disagreement(predictions, "1y") is False
    
    def test_calculate_consensus_method(self):
        """calculate_consensus 메서드 테스트"""
        engine = EnsembleEngine()
        
        predictions = {
            "model1": ModelPrediction(
                model_name="model1",
                predictions={
                    "1d": PeriodPrediction(price=100.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model2": ModelPrediction(
                model_name="model2",
                predictions={
                    "1d": PeriodPrediction(price=110.0, reason="상승", sentiment=SentimentType.POSITIVE)
                },
                success=True
            ),
            "model3": ModelPrediction(
                model_name="model3",
                predictions={
                    "1d": PeriodPrediction(price=90.0, reason="하락", sentiment=SentimentType.NEGATIVE)
                },
                success=True
            )
        }
        
        # 긍정이 다수
        consensus = engine.calculate_consensus(predictions, "1d")
        assert consensus == "긍정"
        
        # 존재하지 않는 기간
        consensus = engine.calculate_consensus(predictions, "1y")
        assert consensus == "중립"
