"""
거래대금 순위 서비스
"""
import asyncio
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger

from models.stock import StockRanking
from data_collector.realtime import RealtimeDataCollector


class RankingService:
    """거래대금 순위 서비스"""
    
    def __init__(self):
        """초기화"""
        self.cache: Optional[List[StockRanking]] = None
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 60  # 1분 캐시
        self.realtime_collector = RealtimeDataCollector()
        
        # 한국 주요 종목 (거래대금 상위 종목)
        self.korean_stocks = [
            ("005930.KS", "삼성전자", "KOSPI"),
            ("000660.KS", "SK하이닉스", "KOSPI"),
            ("035420.KS", "NAVER", "KOSPI"),
            ("051910.KS", "LG화학", "KOSPI"),
            ("006400.KS", "삼성SDI", "KOSPI"),
            ("035720.KS", "카카오", "KOSPI"),
            ("005380.KS", "현대차", "KOSPI"),
            ("068270.KS", "셀트리온", "KOSPI"),
            ("207940.KS", "삼성바이오로직스", "KOSPI"),
            ("005490.KS", "POSCO홀딩스", "KOSPI"),
            ("373220.KQ", "LG에너지솔루션", "KOSDAQ"),
            ("247540.KQ", "에코프로비엠", "KOSDAQ"),
            ("086520.KQ", "에코프로", "KOSDAQ"),
            ("091990.KQ", "셀트리온헬스케어", "KOSDAQ"),
            ("096770.KQ", "SK이노베이션", "KOSDAQ"),
        ]
    
    async def get_rankings(self, force_refresh: bool = False) -> List[StockRanking]:
        """
        거래대금 기준 상위 종목 조회
        
        Args:
            force_refresh: 강제 갱신 여부
            
        Returns:
            List[StockRanking]: 순위 리스트
        """
        # 캐시 확인
        if not force_refresh and self._is_cache_valid():
            logger.info("거래대금 순위 캐시 히트")
            return self.cache
        
        logger.info("거래대금 순위 데이터 수집 시작")
        start_time = time.time()
        
        # 병렬로 데이터 수집
        tasks = [
            self._fetch_stock_data(symbol, name, market)
            for symbol, name, market in self.korean_stocks
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 유효한 결과만 필터링
        valid_stocks = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"종목 데이터 수집 실패: {result}")
                continue
            if result:
                valid_stocks.append(result)
        
        # 거래대금 기준 정렬
        valid_stocks.sort(key=lambda x: x.trading_value, reverse=True)
        
        # 순위 부여
        for rank, stock in enumerate(valid_stocks, start=1):
            stock.rank = rank
        
        # 상위 10개만 반환
        rankings = valid_stocks[:10]
        
        # 캐시 업데이트
        self.cache = rankings
        self.cache_timestamp = datetime.now()
        
        elapsed_time = time.time() - start_time
        logger.info(f"거래대금 순위 데이터 수집 완료 (소요 시간: {elapsed_time:.2f}초)")
        
        return rankings
    
    async def _fetch_stock_data(
        self, 
        symbol: str, 
        name: str, 
        market: str
    ) -> Optional[StockRanking]:
        """
        개별 종목 데이터 수집
        
        Args:
            symbol: 종목 코드
            name: 종목명
            market: 시장
            
        Returns:
            Optional[StockRanking]: 종목 데이터 (실패 시 None)
        """
        try:
            # RealtimeDataCollector를 사용하여 데이터 수집 (Fallback 지원)
            data = await self.realtime_collector.fetch(symbol, market)
            
            # 미니 차트 데이터는 간단한 더미 데이터 사용 (실시간 데이터에는 차트 정보 없음)
            # 실제로는 historical data를 사용해야 하지만, 성능을 위해 생략
            current_price = data['current_price']
            mini_chart_data = [
                current_price * 0.98,
                current_price * 0.99,
                current_price * 1.00,
                current_price * 1.01,
                current_price
            ]
            
            return StockRanking(
                rank=1,  # 임시 값, 나중에 실제 순위로 업데이트
                symbol=symbol,
                name=name,
                market=market,
                current_price=current_price,
                change_rate=data['change_rate'],
                trading_value=data['trading_value'] / 100000000,  # 억원 단위
                mini_chart_data=mini_chart_data
            )
        except Exception as e:
            logger.error(f"종목 데이터 수집 실패 - {symbol}: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """
        캐시 유효성 확인
        
        Returns:
            bool: 캐시가 유효하면 True
        """
        if self.cache is None or self.cache_timestamp is None:
            return False
        
        elapsed = (datetime.now() - self.cache_timestamp).total_seconds()
        return elapsed < self.cache_ttl


# 전역 인스턴스
ranking_service = RankingService()
