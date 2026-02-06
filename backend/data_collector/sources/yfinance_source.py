"""
Yahoo Finance 데이터 소스
"""
import yfinance as yf
import time
from typing import Dict, Optional
from loguru import logger
from .base import DataSource


class YFinanceSource(DataSource):
    """Yahoo Finance 데이터 소스"""
    
    def __init__(self):
        super().__init__(name="YahooFinance", priority=1)
        self._setup_session()
    
    def _setup_session(self):
        """세션 설정"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        
        self.session = session
    
    def supports_market(self, market: str) -> bool:
        """모든 시장 지원"""
        return True
    
    def fetch_realtime(self, symbol: str, market: str) -> Optional[Dict]:
        """실시간 데이터 수집"""
        ticker_symbol = self._format_symbol(symbol, market)
        
        try:
            ticker = yf.Ticker(ticker_symbol, session=self.session)
            
            # 짧은 타임아웃으로 빠르게 시도
            hist = ticker.history(period='5d', timeout=3)
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            volume = int(hist['Volume'].iloc[-1])
            previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            return {
                'current_price': float(current_price),
                'market_cap': 0.0,  # info 요청 생략
                'trading_volume': int(volume),
                'trading_value': float(current_price * volume),
                'change_rate': float((current_price - previous_close) / previous_close * 100) if previous_close else 0.0,
                'previous_close': float(previous_close)
            }
            
        except Exception as e:
            logger.debug(f"YFinance 오류: {str(e)}")
            return None
    
    def _format_symbol(self, symbol: str, market: str) -> str:
        """심볼 형식 변환"""
        market = market.upper()
        
        if '.' in symbol:
            return symbol
        
        if market in ['KRX', 'KOSPI', 'KOSDAQ']:
            if symbol.isdigit() and len(symbol) == 6:
                return f"{symbol}.KS" if market != 'KOSDAQ' else f"{symbol}.KQ"
        
        return symbol
