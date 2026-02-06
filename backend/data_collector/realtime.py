"""
실시간 주식 데이터 수집 모듈
"""
from typing import Dict
from loguru import logger
import asyncio
from .fallback_manager import FallbackManager


class RealtimeDataCollector:
    """실시간 주식 데이터 수집 클래스"""
    
    def __init__(self):
        """초기화"""
        self.fallback_manager = FallbackManager()
        
    async def fetch(self, symbol: str, market: str) -> Dict:
        """
        실시간 주식 데이터 수집
        
        Args:
            symbol: 종목 코드 (예: "035420.KQ", "AAPL")
            market: 시장 (예: "KRX", "NASDAQ")
            
        Returns:
            Dict: 현재가, 시가총액, 거래량, 거래대금 포함
            
        Raises:
            RuntimeError: 데이터 수집 실패
        """
        try:
            # 비동기 실행을 위해 별도 스레드에서 실행
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self.fallback_manager.fetch_with_fallback,
                symbol,
                market
            )
            return data
            
        except Exception as e:
            logger.error(f"실시간 데이터 수집 실패 - 종목: {symbol}, 오류: {e}")
            raise RuntimeError(f"데이터 수집 실패: {str(e)}")
    
    async def fetch_multiple(self, symbols: list[tuple[str, str]]) -> Dict[str, Dict]:
        """
        여러 종목의 실시간 데이터를 병렬로 수집
        
        Args:
            symbols: [(종목코드, 시장), ...] 리스트
            
        Returns:
            Dict[str, Dict]: {종목코드: 데이터} 형태
        """
        tasks = [self.fetch(symbol, market) for symbol, market in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        output = {}
        for (symbol, market), result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.warning(f"종목 {symbol} 데이터 수집 실패: {result}")
                continue
            output[symbol] = result
        
        return output
    
    def get_source_status(self) -> Dict:
        """데이터 소스 상태 조회"""
        return self.fallback_manager.get_status()
    
    def reset_sources(self):
        """모든 데이터 소스 리셋"""
        self.fallback_manager.reset_all_sources()
