import yfinance as yf
import requests

print("=" * 50)
print("Yahoo Finance 연결 테스트")
print("=" * 50)

# 1. 직접 HTTP 요청 테스트
print("\n1. Yahoo Finance API 직접 접근 테스트:")
try:
    url = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    print(f"   상태 코드: {response.status_code}")
    print(f"   응답 길이: {len(response.text)} bytes")
    if response.status_code == 200:
        print("   ✓ 직접 접근 성공")
    else:
        print(f"   ✗ 실패: {response.text[:200]}")
except Exception as e:
    print(f"   ✗ 오류: {e}")

# 2. yfinance 버전 확인
print(f"\n2. yfinance 버전: {yf.__version__}")

# 3. 미국 주식 테스트 (AAPL)
print("\n3. 미국 주식 테스트 (AAPL):")
try:
    ticker = yf.Ticker('AAPL')
    
    # history 메서드 테스트
    print("   - history(period='5d') 테스트...")
    hist = ticker.history(period='5d')
    print(f"     데이터 행 수: {len(hist)}")
    if not hist.empty:
        print(f"     최신 종가: ${hist['Close'].iloc[-1]:.2f}")
        print("     ✓ 성공")
    else:
        print("     ✗ 데이터 없음")
    
    # info 메서드 테스트
    print("   - info 테스트...")
    try:
        info = ticker.info
        if info:
            print(f"     회사명: {info.get('longName', 'N/A')}")
            print(f"     현재가: ${info.get('currentPrice', 'N/A')}")
            print("     ✓ 성공")
        else:
            print("     ✗ info 없음")
    except Exception as e:
        print(f"     ✗ info 오류: {e}")
        
except Exception as e:
    print(f"   ✗ 전체 오류: {e}")

# 4. 한국 주식 테스트 (삼성전자)
print("\n4. 한국 주식 테스트 (005930.KS):")
try:
    ticker = yf.Ticker('005930.KS')
    hist = ticker.history(period='5d')
    print(f"   데이터 행 수: {len(hist)}")
    if not hist.empty:
        print(f"   최신 종가: {hist['Close'].iloc[-1]:,.0f}원")
        print("   ✓ 성공")
    else:
        print("   ✗ 데이터 없음 (시장 휴장 가능성)")
except Exception as e:
    print(f"   ✗ 오류: {e}")

# 5. 다른 기간으로 테스트
print("\n5. 다른 기간 테스트 (AAPL):")
for period in ['1d', '5d', '1mo', '3mo']:
    try:
        ticker = yf.Ticker('AAPL')
        hist = ticker.history(period=period)
        print(f"   period='{period}': {len(hist)}행")
    except Exception as e:
        print(f"   period='{period}': 오류 - {e}")

print("\n" + "=" * 50)
print("테스트 완료")
print("=" * 50)
