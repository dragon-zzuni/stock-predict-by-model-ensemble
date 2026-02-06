"""
데이터 수집 관련 예외 클래스
"""


class DataCollectionError(Exception):
    """데이터 수집 기본 예외"""
    pass


class InvalidSymbolError(DataCollectionError):
    """잘못된 종목 코드 예외"""
    pass


class APITimeoutError(DataCollectionError):
    """API 타임아웃 예외"""
    pass


class APIRateLimitError(DataCollectionError):
    """API 요청 제한 초과 예외"""
    pass


class DataNotFoundError(DataCollectionError):
    """데이터를 찾을 수 없음 예외"""
    pass


class CacheError(Exception):
    """캐시 관련 예외"""
    pass
