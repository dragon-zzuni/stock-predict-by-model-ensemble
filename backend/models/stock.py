"""
주식 관련 데이터 모델
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class Stock(BaseModel):
    """종목 정보"""
    symbol: str = Field(..., description="종목 코드 (예: '035420.KQ')")
    name: str = Field(..., description="종목명 (예: 'NAVER')")
    market: str = Field(..., description="시장 (예: 'KRX', 'NASDAQ')")
    current_price: float = Field(..., gt=0, description="현재가")
    change_rate: float = Field(..., description="등락률 (%)")

    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("종목 코드는 비어있을 수 없습니다")
        return v.strip()

    @validator('market')
    def validate_market(cls, v):
        allowed_markets = ['KRX', 'NASDAQ', 'NYSE', 'KOSPI', 'KOSDAQ']
        if v.upper() not in allowed_markets:
            raise ValueError(f"지원되지 않는 시장입니다: {v}")
        return v.upper()


class StockRanking(Stock):
    """순위 정보를 포함한 종목"""
    rank: int = Field(..., ge=1, description="순위")
    trading_value: float = Field(..., ge=0, description="거래대금 (억원)")
    mini_chart_data: List[float] = Field(default_factory=list, description="미니 차트용 최근 가격 데이터")

    @validator('mini_chart_data')
    def validate_chart_data(cls, v):
        if v and len(v) > 100:
            raise ValueError("차트 데이터는 최대 100개까지 허용됩니다")
        return v
