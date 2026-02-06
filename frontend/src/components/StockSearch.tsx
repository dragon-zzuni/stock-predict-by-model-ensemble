/**
 * 종목 검색 컴포넌트
 * 
 * 검색창 UI, 자동완성 로직, 종목 선택 처리를 담당합니다.
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */

import { useState, useEffect, useRef } from 'react';
import { Stock } from '../types/stock';
import { useAppStore } from '../store/useAppStore';

// 샘플 종목 목록 (실제로는 백엔드 API에서 가져와야 함)
const STOCK_LIST: Stock[] = [
  // 국내 주식 (KOSPI)
  { symbol: '005930.KS', name: '삼성전자', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '000660.KS', name: 'SK하이닉스', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '035420.KS', name: 'NAVER', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '035720.KS', name: '카카오', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '051910.KS', name: 'LG화학', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '006400.KS', name: '삼성SDI', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '207940.KS', name: '삼성바이오로직스', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '005380.KS', name: '현대차', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '000270.KS', name: '기아', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  { symbol: '068270.KS', name: '셀트리온', market: 'KOSPI', currentPrice: 0, changeRate: 0 },
  
  // 국내 주식 (KOSDAQ)
  { symbol: '247540.KQ', name: '에코프로비엠', market: 'KOSDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: '086520.KQ', name: '에코프로', market: 'KOSDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: '091990.KQ', name: '셀트리온헬스케어', market: 'KOSDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: '196170.KQ', name: '알테오젠', market: 'KOSDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: '066970.KQ', name: '엘앤에프', market: 'KOSDAQ', currentPrice: 0, changeRate: 0 },
  
  // 해외 주식 (NASDAQ)
  { symbol: 'AAPL', name: 'Apple Inc.', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'MSFT', name: 'Microsoft Corporation', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'NVDA', name: 'NVIDIA Corporation', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'TSLA', name: 'Tesla Inc.', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
  { symbol: 'META', name: 'Meta Platforms Inc.', market: 'NASDAQ', currentPrice: 0, changeRate: 0 },
];

export const StockSearch = () => {
  const { selectedStock, setSelectedStock } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<Stock[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const searchRef = useRef<HTMLDivElement>(null);

  // 검색어 변경 시 자동완성 목록 업데이트
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    // 검색어와 매칭되는 종목 필터링
    const query = searchQuery.toLowerCase();
    const filtered = STOCK_LIST.filter(
      (stock) =>
        stock.name.toLowerCase().includes(query) ||
        stock.symbol.toLowerCase().includes(query)
    );

    setSuggestions(filtered);
    setShowSuggestions(filtered.length > 0);
    setHighlightedIndex(-1);
  }, [searchQuery]);

  // 외부 클릭 시 자동완성 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 종목 선택 처리
  const handleSelectStock = (stock: Stock) => {
    setSelectedStock(stock);
    setSearchQuery(`${stock.name} (${stock.symbol})`);
    setShowSuggestions(false);
    setHighlightedIndex(-1);
  };

  // 키보드 네비게이션
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
          handleSelectStock(suggestions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // 검색창 초기화
  const handleClear = () => {
    setSearchQuery('');
    setSelectedStock(null);
    setSuggestions([]);
    setShowSuggestions(false);
    setHighlightedIndex(-1);
  };

  return (
    <div className="relative" ref={searchRef}>
      <label htmlFor="stock-search" className="block text-sm font-medium text-gray-700 mb-2">
        종목 검색
      </label>
      
      <div className="relative">
        <input
          id="stock-search"
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (suggestions.length > 0) {
              setShowSuggestions(true);
            }
          }}
          placeholder="종목명 또는 종목코드를 입력하세요"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
        />
        
        {/* 검색창 아이콘 */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
          {searchQuery && (
            <button
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="검색어 지우기"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* 자동완성 드롭다운 */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((stock, index) => (
            <button
              key={stock.symbol}
              onClick={() => handleSelectStock(stock)}
              className={`w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors ${
                index === highlightedIndex ? 'bg-blue-50' : ''
              } ${index !== suggestions.length - 1 ? 'border-b border-gray-100' : ''}`}
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium text-gray-900">{stock.name}</div>
                  <div className="text-sm text-gray-500">{stock.symbol}</div>
                </div>
                <div className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                  {stock.market}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 선택된 종목 표시 */}
      {selectedStock && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm text-gray-600">선택된 종목</div>
              <div className="font-medium text-gray-900">
                {selectedStock.name} ({selectedStock.symbol})
              </div>
              <div className="text-xs text-gray-500 mt-1">{selectedStock.market}</div>
            </div>
            <button
              onClick={handleClear}
              className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
            >
              변경
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
