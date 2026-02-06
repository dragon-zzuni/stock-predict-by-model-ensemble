/**
 * API 서비스 레이어
 * Axios를 사용하여 백엔드 API와 통신
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import { StockRanking } from '../types/stock';
import { PredictionResult } from '../types/prediction';

/**
 * 예측 요청 파라미터
 */
export interface PredictRequest {
  symbol: string;
  market: string;
}

/**
 * API 오류 응답
 */
export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: string;
    timestamp?: string;
    retryable?: boolean;
  };
}

/**
 * Axios 인스턴스 생성
 */
const createApiClient = (): AxiosInstance => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const client = axios.create({
    baseURL,
    timeout: 30000, // 30초 타임아웃
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 요청 인터셉터: 로깅 및 인증 토큰 추가 (필요시)
  client.interceptors.request.use(
    (config) => {
      if (import.meta.env.VITE_DEBUG_MODE === 'true') {
        console.log('[API Request]', config.method?.toUpperCase(), config.url);
      }
      return config;
    },
    (error) => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // 응답 인터셉터: 오류 처리
  client.interceptors.response.use(
    (response) => {
      if (import.meta.env.VITE_DEBUG_MODE === 'true') {
        console.log('[API Response]', response.status, response.config.url);
      }
      return response;
    },
    (error: AxiosError<ApiError>) => {
      console.error('[API Response Error]', error.response?.status, error.message);
      
      // 오류 메시지 추출
      let errorMessage = '알 수 없는 오류가 발생했습니다.';
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error.message;
      } else if (error.message) {
        errorMessage = error.message;
      }

      // 네트워크 오류 처리
      if (!error.response) {
        errorMessage = '네트워크 연결을 확인해주세요.';
      }

      return Promise.reject(new Error(errorMessage));
    }
  );

  return client;
};

/**
 * API 클라이언트 인스턴스
 */
const apiClient = createApiClient();

/**
 * API 서비스 객체
 */
export const apiService = {
  /**
   * 거래대금 상위 종목 조회
   * @returns 순위 데이터 배열
   */
  async getRankings(): Promise<StockRanking[]> {
    try {
      const response = await apiClient.get<{ rankings: any[] }>('/rankings');
      // snake_case를 camelCase로 변환
      return response.data.rankings.map((item: any) => ({
        symbol: item.symbol,
        name: item.name,
        market: item.market,
        currentPrice: item.current_price,
        changeRate: item.change_rate,
        rank: item.rank,
        tradingValue: item.trading_value,
        miniChartData: item.mini_chart_data,
      }));
    } catch (error) {
      console.error('순위 조회 실패:', error);
      throw error;
    }
  },

  /**
   * 주가 예측 요청
   * @param request 예측 요청 파라미터
   * @returns 예측 결과
   */
  async predict(request: PredictRequest): Promise<PredictionResult> {
    try {
      const response = await apiClient.post<PredictionResult>('/predict', request);
      return response.data;
    } catch (error) {
      console.error('예측 요청 실패:', error);
      throw error;
    }
  },

  /**
   * 서버 상태 확인
   * @returns 서버 상태 정보
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('서버 상태 확인 실패:', error);
      throw error;
    }
  },
};

/**
 * API 오류 타입 가드
 */
export const isApiError = (error: unknown): error is AxiosError<ApiError> => {
  return axios.isAxiosError(error) && error.response?.data?.error !== undefined;
};

/**
 * 재시도 가능한 오류인지 확인
 */
export const isRetryableError = (error: unknown): boolean => {
  if (isApiError(error)) {
    return error.response?.data?.error?.retryable ?? false;
  }
  // 네트워크 오류는 재시도 가능
  return !axios.isAxiosError(error) || !error.response;
};
