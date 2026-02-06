/**
 * Zustand 기반 전역 상태 관리 스토어
 */

import { create } from 'zustand';
import { Stock, StockRanking } from '../types/stock';
import { PredictionResult } from '../types/prediction';

/**
 * 애플리케이션 전역 상태 인터페이스
 */
interface AppState {
  // 상태
  selectedStock: Stock | null;
  predictions: PredictionResult | null;
  rankings: StockRanking[];
  loading: boolean;
  error: string | null;

  // 액션
  setSelectedStock: (stock: Stock | null) => void;
  setPredictions: (predictions: PredictionResult | null) => void;
  setRankings: (rankings: StockRanking[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  reset: () => void;
}

/**
 * 초기 상태
 */
const initialState = {
  selectedStock: null,
  predictions: null,
  rankings: [],
  loading: false,
  error: null,
};

/**
 * Zustand 스토어 생성
 */
export const useAppStore = create<AppState>((set) => ({
  ...initialState,

  // 선택된 종목 설정
  setSelectedStock: (stock) => set({ selectedStock: stock }),

  // 예측 결과 설정
  setPredictions: (predictions) => set({ predictions }),

  // 순위 데이터 설정
  setRankings: (rankings) => set({ rankings }),

  // 로딩 상태 설정
  setLoading: (loading) => set({ loading }),

  // 오류 메시지 설정
  setError: (error) => set({ error }),

  // 오류 메시지 초기화
  clearError: () => set({ error: null }),

  // 전체 상태 초기화
  reset: () => set(initialState),
}));
