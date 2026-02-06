import yfinance as yf

# AAPL 테스트
ticker = yf.Ticker('AAPL')
hist = ticker.history(period='1mo')
print(f'Data available: {not hist.empty}')
if not hist.empty:
    print(f'Latest close: {hist["Close"].iloc[-1]}')
    print(f'Latest volume: {hist["Volume"].iloc[-1]}')
