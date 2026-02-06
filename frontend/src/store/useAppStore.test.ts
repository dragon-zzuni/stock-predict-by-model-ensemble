/**
 * Zustand 스토어 테스트
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useAppStore } from './useAppStore';
import { Stock, StockRanking } from '../types/stock';

describe('useAppStore', () => {
  beforeEach(() => {
    // 각 테스트 전에 스토어 초기화
    useAppStore.getState().reset();
  });

  it('초기 상태가 올바르게 설정되어야 함', () => {
    const state = useAppStore.getState();
    
    expect(state.selectedStock).toBeNull();
    expect(state.predictions).toBeNull();
    expect(state.rankings).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('선택된 종목을 설정할 수 있어야 함', () => {
    const stock: Stock = {
      symbol: '035420.KQ',
      name: 'NAVER',
      market: 'KRX',
      currentPrice: 200000,
      changeRate: 2.5,
    };

    useAppStore.getState().setSelectedStock(stock);
    
    expect(useAppStore.getState().selectedStock).toEqual(stock);
  });

  it('순위 데이터를 설정할 수 있어야 함', () => {
    const rankings: StockRanking[] = [
      {
        rank: 1,
        symbol: '005930.KS',
        name: '삼성전자',
        market: 'KRX',
        currentPrice: 70000,
        changeRate: 1.5,
        tradingValue: 5000,
        miniChartData: [69000, 69500, 70000],
      },
    ];

    useAppStore.getState().setRankings(rankings);
    
    expect(useAppStore.getState().rankings).toEqual(rankings);
  });

  it('로딩 상태를 설정할 수 있어야 함', () => {
    useAppStore.getState().setLoading(true);
    expect(useAppStore.getState().loading).toBe(true);

    useAppStore.getState().setLoading(false);
    expect(useAppStore.getState().loading).toBe(false);
  });

  it('오류 메시지를 설정하고 초기화할 수 있어야 함', () => {
    const errorMessage = '데이터 조회 실패';
    
    useAppStore.getState().setError(errorMessage);
    expect(useAppStore.getState().error).toBe(errorMessage);

    useAppStore.getState().clearError();
    expect(useAppStore.getState().error).toBeNull();
  });

  it('reset 함수가 모든 상태를 초기화해야 함', () => {
    // 상태 변경
    useAppStore.getState().setSelectedStock({
      symbol: '035420.KQ',
      name: 'NAVER',
      market: 'KRX',
      currentPrice: 200000,
      changeRate: 2.5,
    });
    useAppStore.getState().setLoading(true);
    useAppStore.getState().setError('테스트 오류');

    // 초기화
    useAppStore.getState().reset();

    // 검증
    const state = useAppStore.getState();
    expect(state.selectedStock).toBeNull();
    expect(state.predictions).toBeNull();
    expect(state.rankings).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });
});
