"""
데이터 수집 모듈

이 모듈은 주식 데이터 수집을 위한 다양한 클래스를 제공합니다:
- DataCollector: 통합 데이터 수집 클래스
- RealtimeDataCollector: 실시간 데이터 수집
- HistoricalDataCollector: 과거 데이터 수집
- NewsCollector: 뉴스 및 감성 분석
- CacheManager: 데이터 캐싱 관리
"""

from data_collector.collector import DataCollector
from data_collector.realtime import RealtimeDataCollector
from data_collector.historical import HistoricalDataCollector
from data_collector.news import NewsCollector
from data_collector.cache import CacheManager
from data_collector.exceptions import (
    DataCollectionError,
    InvalidSymbolError,
    APITimeoutError,
    APIRateLimitError,
    DataNotFoundError,
    CacheError
)

__all__ = [
    'DataCollector',
    'RealtimeDataCollector',
    'HistoricalDataCollector',
    'NewsCollector',
    'CacheManager',
    'DataCollectionError',
    'InvalidSymbolError',
    'APITimeoutError',
    'APIRateLimitError',
    'DataNotFoundError',
    'CacheError'
]
