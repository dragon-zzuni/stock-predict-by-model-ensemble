"""
AI 예측 관련 모델
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class SentimentType(str, Enum):
    """감성 타입"""
    POSITIVE = "긍정"
    NEGATIVE = "부정"
    NEUTRAL = "중립"


class PeriodPrediction(BaseModel):
    """기간별 예측"""
    price: float = Field(..., gt=0, description="예측 가격")
    reason: str = Field(..., min_length=1, description="예측 근거")
    sentiment: SentimentType = Field(..., description="감성 지표")

    @validator('reason')
    def validate_reason(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("예측 근거는 비어있을 수 없습니다")
        return v.strip()


class ModelPrediction(BaseModel):
    """개별 모델의 예측 결과"""
    model_name: str = Field(..., description="모델명")
    predictions: Dict[str, PeriodPrediction] = Field(..., description="기간별 예측 (1d, 1w, 1m)")
    timestamp: datetime = Field(default_factory=datetime.now, description="예측 시각")
    success: bool = Field(default=True, description="예측 성공 여부")

    @validator('predictions')
    def validate_predictions(cls, v):
        # 최소 하나 이상의 기간 예측이 있어야 함
        if not v or len(v) == 0:
            raise ValueError("최소 하나 이상의 기간 예측이 필요합니다")
        return v

    @validator('model_name')
    def validate_model_name(cls, v):
        # 모델명 검증을 완화 - 테스트 및 확장성을 위해
        if not v or len(v.strip()) == 0:
            raise ValueError("모델명은 비어있을 수 없습니다")
        return v
