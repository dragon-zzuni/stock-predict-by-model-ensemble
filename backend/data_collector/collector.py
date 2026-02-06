"""
통합 데이터 수집 모듈
"""
import asyncio
from typing import Dict, Optional
from loguru import logger
import time

from data_collector.realtime import RealtimeDataCollector
from data_collector.historical import HistoricalDataCollector
from data_collector.news import NewsCollector
from data_collector.cache import CacheManager
from data_collector.exceptions import (
    InvalidSymbolError,
    APITimeoutError,
    DataNotFoundError
)
from models.data import CollectedData


class DataCollector:
    """통합 데이터 수집 클래스"""
    
    def __init__(self, cache_dir: str = "backend/cache"):
        """
        초기화
        
        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.realtime = RealtimeDataCollector()
        self.historical = HistoricalDataCollector()
        self.news = NewsCollector()
        self.cache = CacheManager(cache_dir)
        
        # 재시도 설정
        self.max_retries = 3
        self.retry_delay = 1  # 초
        
        logger.info("DataCollector 초기화 완료")
    
    async def collect_all(self, symbol: str, market: str, company_name: str = "") -> CollectedData:
        """
        모든 필요한 데이터를 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            company_name: 회사명 (선택)
            
        Returns:
            CollectedData: 수집된 종합 데이터
            
        Raises:
            InvalidSymbolError: 잘못된 종목 코드
            DataNotFoundError: 데이터를 찾을 수 없음
            RuntimeError: 데이터 수집 실패
        """
        logger.info(f"데이터 수집 시작: {symbol} ({market})")
        start_time = time.time()
        
        # 종목 코드 검증
        self._validate_symbol(symbol, market)
        
        try:
            # 병렬로 데이터 수집
            realtime_data, historical_data, news_data = await asyncio.gather(
                self._fetch_realtime_with_retry(symbol, market),
                self._fetch_historical_with_cache(symbol, market),
                self._fetch_news_with_retry(symbol, company_name),
                return_exceptions=True
            )
            
            # 오류 처리
            if isinstance(realtime_data, Exception):
                logger.error(f"실시간 데이터 수집 실패: {realtime_data}")
                raise RuntimeError(f"실시간 데이터 수집 실패: {str(realtime_data)}")
            
            if isinstance(historical_data, Exception):
                logger.warning(f"과거 데이터 수집 실패: {historical_data}")
                historical_data = {'daily': [], 'weekly': [], 'monthly': []}
            
            if isinstance(news_data, Exception):
                logger.warning(f"뉴스 데이터 수집 실패: {news_data}")
                news_data = {
                    'news_summary': '뉴스 데이터를 가져올 수 없습니다.',
                    'sentiment_score': 0.0,
                    'news_count': 0
                }
            
            # 기술적 지표 계산
            technical_indicators = {}
            if historical_data.get('daily'):
                technical_indicators = self.historical.calculate_technical_indicators(
                    historical_data['daily']
                )
            
            # CollectedData 객체 생성
            collected_data = CollectedData(
                symbol=symbol,
                name=company_name or symbol,
                current_price=realtime_data['current_price'],
                market_cap=realtime_data['market_cap'],
                trading_volume=realtime_data['trading_volume'],
                trading_value=realtime_data['trading_value'],
                change_rate=realtime_data['change_rate'],
                historical_prices=historical_data.get('daily', []),
                technical_indicators=technical_indicators,
                news_summary=news_data['news_summary'],
                sentiment_score=news_data['sentiment_score'],
                news_count=news_data['news_count']
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"데이터 수집 완료: {symbol} (소요 시간: {elapsed_time:.2f}초)")
            
            return collected_data
            
        except Exception as e:
            logger.error(f"데이터 수집 중 오류 발생: {symbol}, 오류: {e}")
            raise
    
    async def _fetch_realtime_with_retry(self, symbol: str, market: str) -> Dict:
        """
        재시도 로직을 포함한 실시간 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: 실시간 데이터
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                data = await self.realtime.fetch(symbol, market)
                return data
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"실시간 데이터 수집 실패 (시도 {attempt + 1}/{self.max_retries}): {e}"
                )
                
                if attempt < self.max_retries - 1:
                    # 지수 백오프
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # 모든 재시도 실패
        raise RuntimeError(f"실시간 데이터 수집 실패 (최대 재시도 초과): {last_error}")
    
    async def _fetch_historical_with_cache(self, symbol: str, market: str) -> Dict:
        """
        캐시를 활용한 과거 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: 과거 데이터 (일봉, 주봉, 월봉)
        """
        cache_key = f"historical:{symbol}:{market}"
        
        # 캐시 조회
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"과거 데이터 캐시 히트: {symbol}")
            return cached_data
        
        # 캐시 미스 - 데이터 수집
        logger.info(f"과거 데이터 캐시 미스: {symbol}, 새로 수집합니다")
        data = await self.historical.fetch(symbol, market)
        
        # 캐시 저장 (1일 TTL)
        # OHLCV 객체를 dict로 변환하여 저장
        cacheable_data = {
            'daily': [ohlcv.dict() for ohlcv in data['daily']],
            'weekly': [ohlcv.dict() for ohlcv in data['weekly']],
            'monthly': [ohlcv.dict() for ohlcv in data['monthly']]
        }
        self.cache.set(cache_key, cacheable_data, ttl=86400)  # 1일
        
        return data
    
    async def _fetch_news_with_retry(self, symbol: str, company_name: str) -> Dict:
        """
        재시도 로직을 포함한 뉴스 데이터 수집
        
        Args:
            symbol: 종목 코드
            company_name: 회사명
            
        Returns:
            Dict: 뉴스 및 감성 분석 결과
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                data = await self.news.fetch_and_analyze(symbol, company_name)
                return data
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"뉴스 데이터 수집 실패 (시도 {attempt + 1}/{self.max_retries}): {e}"
                )
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # 모든 재시도 실패 - 기본값 반환 (뉴스는 필수가 아님)
        logger.warning(f"뉴스 데이터 수집 실패 (최대 재시도 초과): {last_error}")
        return {
            'news_summary': '뉴스 데이터를 가져올 수 없습니다.',
            'sentiment_score': 0.0,
            'news_count': 0
        }
    
    def _validate_symbol(self, symbol: str, market: str):
        """
        종목 코드 검증
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Raises:
            InvalidSymbolError: 잘못된 종목 코드
        """
        if not symbol or not symbol.strip():
            raise InvalidSymbolError("종목 코드가 비어있습니다")
        
        market = market.upper()
        allowed_markets = ['KRX', 'KOSPI', 'KOSDAQ', 'NASDAQ', 'NYSE']
        
        if market not in allowed_markets:
            raise InvalidSymbolError(f"지원되지 않는 시장입니다: {market}")
        
        # 한국 시장 종목 코드 검증
        if market in ['KRX', 'KOSPI', 'KOSDAQ']:
            # 6자리 숫자 또는 .KS/.KQ 형식
            clean_symbol = symbol.split('.')[0]
            if not (clean_symbol.isdigit() and len(clean_symbol) == 6):
                if '.' not in symbol:
                    raise InvalidSymbolError(
                        f"한국 시장 종목 코드는 6자리 숫자여야 합니다: {symbol}"
                    )
        
        logger.debug(f"종목 코드 검증 통과: {symbol} ({market})")
