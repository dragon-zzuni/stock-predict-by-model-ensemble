"""
과거 주식 데이터 수집 모듈
"""
import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio
from models.data import OHLCV


class HistoricalDataCollector:
    """과거 주식 데이터 수집 클래스"""
    
    def __init__(self):
        """초기화"""
        self.max_years = 5  # 최대 5년치 데이터
        
    async def fetch(self, symbol: str, market: str) -> Dict[str, List[OHLCV]]:
        """
        과거 주식 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: {'daily': [...], 'weekly': [...], 'monthly': [...]}
            
        Raises:
            RuntimeError: 데이터 수집 실패
        """
        try:
            # 비동기 실행
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._fetch_sync, symbol, market)
            return data
            
        except Exception as e:
            logger.error(f"과거 데이터 수집 실패 - 종목: {symbol}, 오류: {e}")
            raise RuntimeError(f"과거 데이터 수집 실패: {str(e)}")
    
    def _fetch_sync(self, symbol: str, market: str) -> Dict[str, List[OHLCV]]:
        """
        동기 방식으로 과거 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: 일봉, 주봉, 월봉 데이터
        """
        # 시장별 심볼 형식 조정
        ticker_symbol = self._format_symbol(symbol, market)
        
        logger.info(f"과거 데이터 수집 시작: {ticker_symbol} (최대 {self.max_years}년)")
        
        # yfinance Ticker 객체 생성
        ticker = yf.Ticker(ticker_symbol)
        
        # 5년치 일봉 데이터 수집
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.max_years * 365)
        
        daily_df = ticker.history(start=start_date, end=end_date, interval="1d")
        
        if daily_df.empty:
            raise ValueError(f"과거 데이터를 찾을 수 없습니다: {symbol}")
        
        # 일봉 데이터 변환
        daily_data = self._convert_to_ohlcv(daily_df)
        
        # 주봉 데이터 생성 (일봉 데이터를 주 단위로 리샘플링)
        weekly_df = self._resample_to_weekly(daily_df)
        weekly_data = self._convert_to_ohlcv(weekly_df)
        
        # 월봉 데이터 생성 (일봉 데이터를 월 단위로 리샘플링)
        monthly_df = self._resample_to_monthly(daily_df)
        monthly_data = self._convert_to_ohlcv(monthly_df)
        
        logger.info(
            f"과거 데이터 수집 완료: {ticker_symbol} - "
            f"일봉: {len(daily_data)}개, 주봉: {len(weekly_data)}개, 월봉: {len(monthly_data)}개"
        )
        
        return {
            'daily': daily_data,
            'weekly': weekly_data,
            'monthly': monthly_data
        }
    
    def _convert_to_ohlcv(self, df: pd.DataFrame) -> List[OHLCV]:
        """
        pandas DataFrame을 OHLCV 모델 리스트로 변환
        
        Args:
            df: pandas DataFrame (yfinance 형식)
            
        Returns:
            List[OHLCV]: OHLCV 객체 리스트
        """
        ohlcv_list = []
        
        for index, row in df.iterrows():
            try:
                ohlcv = OHLCV(
                    date=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else index,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                ohlcv_list.append(ohlcv)
            except Exception as e:
                logger.warning(f"OHLCV 변환 실패 (날짜: {index}): {e}")
                continue
        
        return ohlcv_list
    
    def _resample_to_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        일봉 데이터를 주봉으로 리샘플링
        
        Args:
            df: 일봉 DataFrame
            
        Returns:
            pd.DataFrame: 주봉 DataFrame
        """
        weekly = df.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        return weekly
    
    def _resample_to_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        일봉 데이터를 월봉으로 리샘플링
        
        Args:
            df: 일봉 DataFrame
            
        Returns:
            pd.DataFrame: 월봉 DataFrame
        """
        monthly = df.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        return monthly
    
    def _format_symbol(self, symbol: str, market: str) -> str:
        """
        시장별 심볼 형식 변환
        
        Args:
            symbol: 원본 종목 코드
            market: 시장
            
        Returns:
            str: yfinance 형식의 종목 코드
        """
        market = market.upper()
        
        if '.' in symbol:
            return symbol
        
        if market in ['KRX', 'KOSPI', 'KOSDAQ']:
            if symbol.isdigit() and len(symbol) == 6:
                if market == 'KOSDAQ':
                    return f"{symbol}.KQ"
                else:
                    return f"{symbol}.KS"
            return symbol
        
        elif market in ['NASDAQ', 'NYSE']:
            return symbol
        
        return symbol
    
    def calculate_technical_indicators(self, daily_data: List[OHLCV]) -> Dict[str, float]:
        """
        기술적 지표 계산
        
        Args:
            daily_data: 일봉 OHLCV 데이터
            
        Returns:
            Dict: 기술적 지표 (MA20, MA50, RSI 등)
        """
        if not daily_data or len(daily_data) < 20:
            return {}
        
        # 종가 리스트 추출
        closes = [ohlcv.close for ohlcv in daily_data]
        
        indicators = {}
        
        # 이동평균 계산
        if len(closes) >= 20:
            indicators['MA20'] = sum(closes[-20:]) / 20
        
        if len(closes) >= 50:
            indicators['MA50'] = sum(closes[-50:]) / 50
        
        # RSI 계산 (14일 기준)
        if len(closes) >= 15:
            rsi = self._calculate_rsi(closes, period=14)
            if rsi is not None:
                indicators['RSI'] = rsi
        
        return indicators
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        RSI (Relative Strength Index) 계산
        
        Args:
            prices: 가격 리스트
            period: RSI 기간 (기본 14일)
            
        Returns:
            float: RSI 값 (0-100)
        """
        if len(prices) < period + 1:
            return None
        
        # 가격 변화 계산
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 상승/하락 분리
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        # 평균 계산
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
