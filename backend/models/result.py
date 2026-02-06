"""
최종 예측 결과 모델
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
from datetime import datetime
from .prediction import PeriodPrediction, SentimentType


class EnsemblePrediction(PeriodPrediction):
    """앙상블 예측 (종합 예측)"""
    disagreement: bool = Field(default=False, description="모델 간 의견 불일치 여부")
    std_dev: float = Field(default=0.0, ge=0, description="표준편차")

    @validator('disagreement')
    def validate_disagreement(cls, v, values):
        # 표준편차가 평균의 20%를 초과하면 의견 불일치
        if 'std_dev' in values and 'price' in values:
            threshold = values['price'] * 0.2
            if values['std_dev'] > threshold:
                return True
        return v


class PredictionResult(BaseModel):
    """최종 예측 결과"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    current_price: float = Field(..., gt=0, description="현재가")
    predictions: Dict[str, Dict[str, PeriodPrediction]] = Field(
        ..., 
        description="모델별 예측 {model_name: {period: PeriodPrediction}}"
    )
    ensemble: Dict[str, EnsemblePrediction] = Field(
        ..., 
        description="종합 예측 {period: EnsemblePrediction}"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="예측 시각")

    @validator('predictions')
    def validate_predictions(cls, v):
        if not v:
            raise ValueError("최소 하나 이상의 모델 예측이 필요합니다")
        
        # 각 모델이 필수 기간을 포함하는지 확인
        required_periods = {'1d', '1w', '1m'}
        for model_name, periods in v.items():
            if not required_periods.issubset(periods.keys()):
                raise ValueError(f"{model_name} 모델의 필수 기간이 누락되었습니다")
        
        return v

    @validator('ensemble')
    def validate_ensemble(cls, v):
        required_periods = {'1d', '1w', '1m'}
        if not required_periods.issubset(v.keys()):
            raise ValueError(f"종합 예측의 필수 기간이 누락되었습니다: {required_periods - v.keys()}")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
