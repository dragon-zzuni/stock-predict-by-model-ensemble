"""
Alpha Vantage 데이터 소스
"""
import requests
from typing import Dict, Optional
from loguru import logger
from .base import DataSource
from config import settings


class AlphaVantageSource(DataSource):
    """Alpha Vantage 데이터 소스"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="AlphaVantage", priority=4)
        self.api_key = api_key or getattr(settings, 'alpha_vantage_api_key', None)
        self.base_url = "https://www.alphavantage.co/query"
        self.enabled = bool(self.api_key)
    
    def supports_market(self, market: str) -> bool:
        """미국 시장만 지원"""
        return market.upper() in ['NASDAQ', 'NYSE', 'AMEX']
    
    def fetch_realtime(self, symbol: str, market: str) -> Optional[Dict]:
        """실시간 데이터 수집"""
        if not self.api_key:
            return None
        
        try:
            # Global Quote API 사용
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'Global Quote' not in data or not data['Global Quote']:
                return None
            
            quote = data['Global Quote']
            
            current_price = float(quote.get('05. price', 0))
            previous_close = float(quote.get('08. previous close', 0))
            volume = int(quote.get('06. volume', 0))
            
            if current_price == 0:
                return None
            
            return {
                'current_price': current_price,
                'market_cap': 0.0,
                'trading_volume': volume,
                'trading_value': current_price * volume,
                'change_rate': ((current_price - previous_close) / previous_close * 100) if previous_close else 0.0,
                'previous_close': previous_close
            }
            
        except Exception as e:
            logger.debug(f"AlphaVantage 오류: {str(e)[:100]}")
            return None
