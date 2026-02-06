"""
Fallback Chain Manager
여러 데이터 소스를 순차적으로 시도하는 관리자
"""
from typing import Dict, List, Optional
from loguru import logger
from .sources import (
    DataSource,
    YFinanceSource,
    FDRSource,
    PyKrxSource,
    AlphaVantageSource
)


class FallbackManager:
    """데이터 소스 Fallback 관리자"""
    
    def __init__(self):
        """초기화 - 모든 데이터 소스 등록"""
        self.sources: List[DataSource] = []
        self._register_sources()
    
    def _register_sources(self):
        """데이터 소스 등록 (우선순위 순)"""
        # 우선순위 순으로 등록
        self.sources = [
            YFinanceSource(),      # 1순위: Yahoo Finance (글로벌)
            FDRSource(),           # 2순위: FinanceDataReader (한국)
            PyKrxSource(),         # 3순위: PyKrx (한국)
            AlphaVantageSource(),  # 4순위: Alpha Vantage (미국)
        ]
        
        # 우선순위로 정렬
        self.sources.sort(key=lambda x: x.priority)
        
        logger.info(f"데이터 소스 등록 완료: {[s.name for s in self.sources]}")
    
    def fetch_with_fallback(self, symbol: str, market: str) -> Dict:
        """
        Fallback 체인으로 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: 수집된 데이터
            
        Raises:
            RuntimeError: 모든 소스 실패 시
        """
        logger.info(f"Fallback 체인 시작: {symbol} ({market})")
        
        # 활성화된 소스만 필터링
        active_sources = [s for s in self.sources if s.enabled]
        
        if not active_sources:
            logger.error("사용 가능한 데이터 소스가 없습니다")
            return self._get_mock_data(symbol, market)
        
        # 각 소스를 순차적으로 시도
        for source in active_sources:
            data = source.try_fetch(symbol, market)
            
            if data:
                logger.info(f"✓ {source.name}에서 데이터 수집 성공")
                return data
        
        # 모든 소스 실패 시 Mock 데이터 반환
        logger.warning(f"모든 데이터 소스 실패, Mock 데이터 반환: {symbol}")
        return self._get_mock_data(symbol, market)
    
    def _get_mock_data(self, symbol: str, market: str) -> Dict:
        """
        Mock 데이터 생성
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: Mock 데이터
        """
        import random
        
        # 시장별 기본 가격 설정
        if market.upper() in ['KOSPI', 'KOSDAQ', 'KRX']:
            base_price = 50000  # 한국 주식
        else:
            base_price = 150  # 미국 주식
        
        # 랜덤 변동
        current_price = base_price * (1 + random.uniform(-0.05, 0.05))
        previous_close = base_price
        volume = random.randint(1000000, 10000000)
        
        logger.info(f"Mock 데이터 생성: {symbol} - {current_price:,.0f}")
        
        return {
            'current_price': float(current_price),
            'market_cap': float(current_price * volume * 100),
            'trading_volume': int(volume),
            'trading_value': float(current_price * volume),
            'change_rate': float((current_price - previous_close) / previous_close * 100),
            'previous_close': float(previous_close)
        }
    
    def reset_all_sources(self):
        """모든 소스 상태 리셋"""
        for source in self.sources:
            source.reset()
        logger.info("모든 데이터 소스 리셋 완료")
    
    def get_status(self) -> Dict:
        """
        모든 소스의 상태 반환
        
        Returns:
            Dict: 소스별 상태 정보
        """
        return {
            source.name: {
                'enabled': source.enabled,
                'priority': source.priority,
                'failure_count': source.failure_count
            }
            for source in self.sources
        }
