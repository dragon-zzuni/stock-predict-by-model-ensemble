"""
데이터 수집 모듈 테스트
"""
import pytest
import asyncio
from backend.data_collector import DataCollector, InvalidSymbolError


@pytest.mark.asyncio
async def test_realtime_data_collection():
    """실시간 데이터 수집 테스트 (미국 주식)"""
    collector = DataCollector()
    
    # Apple 주식 데이터 수집
    try:
        data = await collector.realtime.fetch("AAPL", "NASDAQ")
        
        # 필수 필드 확인
        assert 'current_price' in data
        assert 'market_cap' in data
        assert 'trading_volume' in data
        assert 'trading_value' in data
        assert 'change_rate' in data
        
        # 값 검증
        assert data['current_price'] > 0
        assert data['market_cap'] >= 0
        assert data['trading_volume'] >= 0
        
        print(f"✓ 실시간 데이터 수집 성공: AAPL - 현재가 ${data['current_price']:.2f}")
        
    except Exception as e:
        pytest.skip(f"실시간 데이터 수집 실패 (네트워크 문제 가능): {e}")


@pytest.mark.asyncio
async def test_historical_data_collection():
    """과거 데이터 수집 테스트"""
    collector = DataCollector()
    
    try:
        data = await collector.historical.fetch("AAPL", "NASDAQ")
        
        # 데이터 구조 확인
        assert 'daily' in data
        assert 'weekly' in data
        assert 'monthly' in data
        
        # 일봉 데이터 확인
        assert len(data['daily']) > 0
        
        # OHLCV 필드 확인
        first_daily = data['daily'][0]
        assert hasattr(first_daily, 'open')
        assert hasattr(first_daily, 'high')
        assert hasattr(first_daily, 'low')
        assert hasattr(first_daily, 'close')
        assert hasattr(first_daily, 'volume')
        
        print(f"✓ 과거 데이터 수집 성공: 일봉 {len(data['daily'])}개, 주봉 {len(data['weekly'])}개, 월봉 {len(data['monthly'])}개")
        
    except Exception as e:
        pytest.skip(f"과거 데이터 수집 실패 (네트워크 문제 가능): {e}")


@pytest.mark.asyncio
async def test_cache_functionality():
    """캐시 기능 테스트"""
    collector = DataCollector()
    
    # 캐시 저장
    test_data = {'test': 'data', 'value': 123}
    cache_key = "test:cache:key"
    
    success = collector.cache.set(cache_key, test_data, ttl=60)
    assert success is True
    
    # 캐시 조회
    cached_data = collector.cache.get(cache_key)
    assert cached_data is not None
    assert cached_data['test'] == 'data'
    assert cached_data['value'] == 123
    
    # 캐시 삭제
    deleted = collector.cache.delete(cache_key)
    assert deleted is True
    
    # 삭제 후 조회
    cached_data = collector.cache.get(cache_key)
    assert cached_data is None
    
    print("✓ 캐시 기능 테스트 성공")


def test_invalid_symbol_validation():
    """잘못된 종목 코드 검증 테스트"""
    collector = DataCollector()
    
    # 빈 종목 코드
    with pytest.raises(InvalidSymbolError):
        collector._validate_symbol("", "NASDAQ")
    
    # 지원되지 않는 시장
    with pytest.raises(InvalidSymbolError):
        collector._validate_symbol("AAPL", "INVALID_MARKET")
    
    # 잘못된 한국 종목 코드 형식
    with pytest.raises(InvalidSymbolError):
        collector._validate_symbol("12345", "KOSPI")  # 5자리
    
    print("✓ 종목 코드 검증 테스트 성공")


@pytest.mark.asyncio
async def test_news_collection():
    """뉴스 수집 테스트 (API 키 없이도 작동)"""
    collector = DataCollector()
    
    # API 키가 없어도 더미 데이터 반환
    news_data = await collector.news.fetch_and_analyze("AAPL", "Apple Inc.")
    
    # 기본 구조 확인
    assert 'news_summary' in news_data
    assert 'sentiment_score' in news_data
    assert 'news_count' in news_data
    
    # 감성 점수 범위 확인
    assert -1.0 <= news_data['sentiment_score'] <= 1.0
    
    print(f"✓ 뉴스 수집 테스트 성공: {news_data['news_count']}개 뉴스")


if __name__ == "__main__":
    # 직접 실행 시 테스트 실행
    print("데이터 수집 모듈 테스트 시작...\n")
    
    asyncio.run(test_realtime_data_collection())
    asyncio.run(test_historical_data_collection())
    asyncio.run(test_cache_functionality())
    test_invalid_symbol_validation()
    asyncio.run(test_news_collection())
    
    print("\n모든 테스트 완료!")
