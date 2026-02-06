"""
데이터 수집 관련 모델
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime


class OHLCV(BaseModel):
    """시가, 고가, 저가, 종가, 거래량 데이터"""
    date: datetime = Field(..., description="날짜")
    open: float = Field(..., gt=0, description="시가")
    high: float = Field(..., gt=0, description="고가")
    low: float = Field(..., gt=0, description="저가")
    close: float = Field(..., gt=0, description="종가")
    volume: int = Field(..., ge=0, description="거래량")

    @validator('high')
    def validate_high(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError("고가는 저가보다 낮을 수 없습니다")
        return v

    @validator('low')
    def validate_low(cls, v, values):
        if 'high' in values and v > values['high']:
            raise ValueError("저가는 고가보다 높을 수 없습니다")
        return v


class CollectedData(BaseModel):
    """수집된 종합 데이터"""
    symbol: str = Field(..., description="종목 코드")
    name: str = Field(..., description="종목명")
    current_price: float = Field(..., gt=0, description="현재가")
    market_cap: float = Field(default=0.0, ge=0, description="시가총액 (0이면 정보 없음)")
    trading_volume: int = Field(..., ge=0, description="거래량")
    trading_value: float = Field(..., ge=0, description="거래대금")
    change_rate: float = Field(..., description="등락률 (%)")
    
    # 과거 데이터
    historical_prices: List[OHLCV] = Field(default_factory=list, description="과거 OHLCV 데이터")
    technical_indicators: Dict[str, float] = Field(default_factory=dict, description="기술적 지표 (MA20, RSI 등)")
    
    # 뉴스 및 감성
    news_summary: str = Field(default="", description="뉴스 요약")
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0, description="감성 점수 (-1.0 ~ 1.0)")
    news_count: int = Field(default=0, ge=0, description="뉴스 개수")

    @validator('historical_prices')
    def validate_historical_prices(cls, v):
        if len(v) > 1825:  # 5년 * 365일
            raise ValueError("과거 데이터는 최대 5년치까지 허용됩니다")
        return v
