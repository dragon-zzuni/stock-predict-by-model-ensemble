/**
 * 예측 관련 타입 정의
 */

/**
 * 감성 타입
 */
export type SentimentType = "긍정" | "부정";

/**
 * 기간별 예측
 */
export interface PeriodPrediction {
  /** 예측 가격 */
  price: number;
  /** 예측 근거 */
  reason: string;
  /** 감성 지표 */
  sentiment: SentimentType;
}

/**
 * 앙상블 예측 (종합 예측)
 */
export interface EnsemblePrediction extends PeriodPrediction {
  /** 모델 간 의견 불일치 여부 */
  disagreement: boolean;
  /** 표준편차 */
  stdDev: number;
}

/**
 * 최종 예측 결과
 */
export interface PredictionResult {
  /** 종목 코드 */
  symbol: string;
  /** 종목명 */
  name: string;
  /** 현재가 */
  currentPrice: number;
  /** 모델별 예측 */
  predictions: {
    [modelName: string]: {
      "1d": PeriodPrediction;
      "1w": PeriodPrediction;
      "1m": PeriodPrediction;
    };
  };
  /** 종합 예측 */
  ensemble: {
    "1d": EnsemblePrediction;
    "1w": EnsemblePrediction;
    "1m": EnsemblePrediction;
  };
  /** 예측 시각 */
  timestamp: string;
}

/**
 * 예측 기간 타입
 */
export type PredictionPeriod = "1d" | "1w" | "1m";

/**
 * AI 모델 이름
 */
export type AIModelName = "GPT-5.2" | "Gemini 3.0" | "Claude 4.5" | "Gemma" | "Qwen";
