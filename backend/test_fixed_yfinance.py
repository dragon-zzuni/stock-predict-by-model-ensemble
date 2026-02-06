import sys
import asyncio
sys.path.insert(0, '.')

from data_collector.realtime import RealtimeDataCollector

async def test():
    collector = RealtimeDataCollector()
    
    print("=" * 50)
    print("수정된 RealtimeDataCollector 테스트")
    print("=" * 50)
    
    # 미국 주식 테스트
    print("\n1. 미국 주식 테스트 (AAPL):")
    try:
        data = await collector.fetch('AAPL', 'NASDAQ')
        print(f"   ✓ 성공!")
        print(f"   현재가: ${data['current_price']:.2f}")
        print(f"   거래량: {data['trading_volume']:,}")
        print(f"   등락률: {data['change_rate']:.2f}%")
    except Exception as e:
        print(f"   ✗ 실패: {e}")
    
    # 한국 주식 테스트
    print("\n2. 한국 주식 테스트 (005930.KS - 삼성전자):")
    try:
        data = await collector.fetch('005930', 'KOSPI')
        print(f"   ✓ 성공!")
        print(f"   현재가: {data['current_price']:,.0f}원")
        print(f"   거래량: {data['trading_volume']:,}")
        print(f"   등락률: {data['change_rate']:.2f}%")
    except Exception as e:
        print(f"   ✗ 실패: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test())
