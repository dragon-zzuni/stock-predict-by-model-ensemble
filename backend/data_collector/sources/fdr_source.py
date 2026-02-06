"""
FinanceDataReader 데이터 소스
"""
from typing import Dict, Optional
from loguru import logger
from .base import DataSource

try:
    import FinanceDataReader as fdr
    FDR_AVAILABLE = True
except ImportError:
    FDR_AVAILABLE = False
    logger.warning("FinanceDataReader가 설치되지 않았습니다")


class FDRSource(DataSource):
    """FinanceDataReader 데이터 소스"""
    
    def __init__(self):
        super().__init__(name="FinanceDataReader", priority=2)
        self.enabled = FDR_AVAILABLE
    
    def supports_market(self, market: str) -> bool:
        """한국 시장만 지원"""
        return market.upper() in ['KRX', 'KOSPI', 'KOSDAQ']
    
    def fetch_realtime(self, symbol: str, market: str) -> Optional[Dict]:
        """실시간 데이터 수집"""
        if not FDR_AVAILABLE:
            return None
        
        try:
            # 6자리 종목 코드로 변환
            ticker_symbol = symbol.replace('.KS', '').replace('.KQ', '')
            
            # 최근 30일 데이터 가져오기
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            df = fdr.DataReader(ticker_symbol, start=start_date)
            
            if df.empty:
                return None
            
            # 최신 데이터
            latest = df.iloc[-1]
            previous = df.iloc[-2] if len(df) > 1 else latest
            
            current_price = float(latest['Close'])
            previous_close = float(previous['Close'])
            volume = int(latest['Volume'])
            
            return {
                'current_price': current_price,
                'market_cap': 0.0,
                'trading_volume': volume,
                'trading_value': current_price * volume,
                'change_rate': ((current_price - previous_close) / previous_close * 100) if previous_close else 0.0,
                'previous_close': previous_close
            }
            
        except Exception as e:
            logger.debug(f"FDR 오류: {str(e)}")
            return None
