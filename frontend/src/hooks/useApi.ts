/**
 * API 호출을 위한 커스텀 훅
 */

import { useState, useCallback } from 'react';
import { apiService, PredictRequest, isRetryableError } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { StockRanking } from '../types/stock';
import { PredictionResult } from '../types/prediction';

/**
 * API 호출 상태
 */
interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/**
 * 순위 조회 훅
 */
export const useRankings = () => {
  const [state, setState] = useState<ApiState<StockRanking[]>>({
    data: null,
    loading: false,
    error: null,
  });

  const setRankings = useAppStore((state) => state.setRankings);

  const fetchRankings = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await apiService.getRankings();
      setState({ data, loading: false, error: null });
      setRankings(data);
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '순위 조회 실패';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, [setRankings]);

  return {
    ...state,
    fetchRankings,
    isRetryable: state.error ? isRetryableError(state.error) : false,
  };
};

/**
 * 예측 요청 훅
 */
export const usePredict = () => {
  const [state, setState] = useState<ApiState<PredictionResult>>({
    data: null,
    loading: false,
    error: null,
  });

  const setPredictions = useAppStore((state) => state.setPredictions);
  const setLoading = useAppStore((state) => state.setLoading);
  const setError = useAppStore((state) => state.setError);

  const predict = useCallback(
    async (request: PredictRequest) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      setLoading(true);
      setError(null);

      try {
        const data = await apiService.predict(request);
        setState({ data, loading: false, error: null });
        setPredictions(data);
        setLoading(false);
        return data;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '예측 요청 실패';
        setState({ data: null, loading: false, error: errorMessage });
        setError(errorMessage);
        setLoading(false);
        throw error;
      }
    },
    [setPredictions, setLoading, setError]
  );

  return {
    ...state,
    predict,
    isRetryable: state.error ? isRetryableError(state.error) : false,
  };
};

/**
 * 서버 상태 확인 훅
 */
export const useHealthCheck = () => {
  const [state, setState] = useState<ApiState<{ status: string; timestamp: string }>>({
    data: null,
    loading: false,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const data = await apiService.healthCheck();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '서버 상태 확인 실패';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    checkHealth,
  };
};
