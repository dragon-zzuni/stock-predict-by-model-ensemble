"""
PyKrx 데이터 소스
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
from .base import DataSource

try:
    from pykrx import stock
    PYKRX_AVAILABLE = True
except ImportError:
    PYKRX_AVAILABLE = False
    logger.warning("pykrx가 설치되지 않았습니다")


class PyKrxSource(DataSource):
    """PyKrx 데이터 소스"""
    
    def __init__(self):
        super().__init__(name="PyKrx", priority=3)
        self.enabled = PYKRX_AVAILABLE
    
    def supports_market(self, market: str) -> bool:
        """한국 시장만 지원"""
        return market.upper() in ['KRX', 'KOSPI', 'KOSDAQ']
    
    def fetch_realtime(self, symbol: str, market: str) -> Optional[Dict]:
        """실시간 데이터 수집"""
        if not PYKRX_AVAILABLE:
            return None
        
        try:
            # 6자리 종목 코드로 변환
            ticker_symbol = symbol.replace('.KS', '').replace('.KQ', '')
            
            # 최근 30일 데이터 가져오기 (주말/공휴일 고려)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            df = stock.get_market_ohlcv_by_date(
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d'),
                ticker_symbol
            )
            
            if df.empty:
                return None
            
            # 최신 데이터
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest
            
            current_price = float(latest['종가'])
            previous_close = float(previous['종가'])
            volume = int(latest['거래량'])
            trading_value = float(latest['거래대금'])
            
            return {
                'current_price': current_price,
                'market_cap': 0.0,
                'trading_volume': volume,
                'trading_value': trading_value,
                'change_rate': ((current_price - previous_close) / previous_close * 100) if previous_close else 0.0,
                'previous_close': previous_close
            }
            
        except Exception as e:
            logger.debug(f"PyKrx 오류: {str(e)}")
            return None
