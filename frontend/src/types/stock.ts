/**
 * 주식 관련 타입 정의
 */

/**
 * 종목 정보
 */
export interface Stock {
  /** 종목 코드 (예: "035420.KQ") */
  symbol: string;
  /** 종목명 (예: "NAVER") */
  name: string;
  /** 시장 (예: "KRX", "NASDAQ") */
  market: string;
  /** 현재가 */
  currentPrice: number;
  /** 등락률 (%) */
  changeRate: number;
}

/**
 * 순위 정보를 포함한 종목
 */
export interface StockRanking extends Stock {
  /** 순위 */
  rank: number;
  /** 거래대금 (억원) */
  tradingValue: number;
  /** 미니 차트용 최근 가격 데이터 */
  miniChartData: number[];
}
