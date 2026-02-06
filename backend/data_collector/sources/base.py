"""
데이터 소스 베이스 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from loguru import logger


class DataSource(ABC):
    """데이터 소스 추상 클래스"""
    
    def __init__(self, name: str, priority: int = 0):
        """
        초기화
        
        Args:
            name: 데이터 소스 이름
            priority: 우선순위 (낮을수록 먼저 시도)
        """
        self.name = name
        self.priority = priority
        self.enabled = True
        self.failure_count = 0
        self.max_failures = 3  # 3번 실패 시 비활성화
    
    @abstractmethod
    def fetch_realtime(self, symbol: str, market: str) -> Optional[Dict]:
        """
        실시간 데이터 수집
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict: {
                'current_price': float,
                'market_cap': float,
                'trading_volume': int,
                'trading_value': float,
                'change_rate': float,
                'previous_close': float
            } 또는 None (실패 시)
        """
        pass
    
    @abstractmethod
    def supports_market(self, market: str) -> bool:
        """
        해당 시장을 지원하는지 확인
        
        Args:
            market: 시장 (예: "KOSPI", "NASDAQ")
            
        Returns:
            bool: 지원 여부
        """
        pass
    
    def try_fetch(self, symbol: str, market: str) -> Optional[Dict]:
        """
        데이터 수집 시도 (에러 처리 포함)
        
        Args:
            symbol: 종목 코드
            market: 시장
            
        Returns:
            Dict 또는 None
        """
        if not self.enabled:
            logger.debug(f"{self.name}: 비활성화됨")
            return None
        
        if not self.supports_market(market):
            logger.debug(f"{self.name}: {market} 시장 미지원")
            return None
        
        try:
            logger.info(f"{self.name}: 데이터 수집 시도 - {symbol} ({market})")
            data = self.fetch_realtime(symbol, market)
            
            if data:
                # 성공 시 실패 카운트 리셋
                self.failure_count = 0
                logger.info(f"{self.name}: ✓ 데이터 수집 성공 - {symbol} - 가격: {data.get('current_price', 0):,.0f}")
                return data
            else:
                logger.warning(f"{self.name}: 데이터 없음 - {symbol}")
                self._record_failure()
                return None
                
        except Exception as e:
            logger.error(f"{self.name}: 오류 발생 - {symbol}: {str(e)}")
            self._record_failure()
            return None
    
    def _record_failure(self):
        """실패 기록 및 비활성화 처리"""
        self.failure_count += 1
        
        if self.failure_count >= self.max_failures:
            self.enabled = False
            logger.warning(
                f"{self.name}: {self.max_failures}번 연속 실패로 비활성화됨"
            )
    
    def reset(self):
        """상태 리셋"""
        self.failure_count = 0
        self.enabled = True
        logger.info(f"{self.name}: 상태 리셋")
