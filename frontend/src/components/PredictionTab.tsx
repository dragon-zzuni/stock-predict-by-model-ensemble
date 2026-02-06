/**
 * 예측 탭 컴포넌트
 * 
 * 예측 버튼, 로딩 상태, 예측 결과 테이블 렌더링을 담당합니다.
 * Requirements: 11.1, 11.2, 11.3, 13.1, 13.2, 13.3
 */

import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { apiService, isRetryableError } from '../services/api';
import { StockSearch } from './StockSearch';
import { PredictionDetailModal } from './PredictionDetailModal';
import { Alert, createErrorAlert } from './Alert';

interface PredictionDetail {
  modelName: string;
  period: string;
  price: number;
  reason: string;
  sentiment: string;
}

export const PredictionTab = () => {
  const { selectedStock, predictions, setPredictions, setError, clearError } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState<PredictionDetail | null>(null);
  const [localError, setLocalError] = useState<Error | null>(null);

  // 예측 실행
  const handlePredict = async () => {
    if (!selectedStock) {
      setError('종목을 먼저 선택해주세요.');
      return;
    }

    setLoading(true);
    setError(null);
    setLocalError(null);

    try {
      const result = await apiService.predict({
        symbol: selectedStock.symbol,
        market: selectedStock.market,
      });

      setPredictions(result);
    } catch (error) {
      const err = error instanceof Error ? error : new Error('예측 요청에 실패했습니다.');
      setLocalError(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 재시도 핸들러
  const handleRetry = () => {
    setLocalError(null);
    clearError();
    handlePredict();
  };

  // 예측 근거 모달 열기
  const handleShowDetail = (modelName: string, period: string, price: number, reason: string, sentiment: string) => {
    setSelectedDetail({
      modelName,
      period,
      price,
      reason,
      sentiment,
    });
  };

  // 모달 닫기
  const handleCloseModal = () => {
    setSelectedDetail(null);
  };

  return (
    <div className="space-y-6">
      {/* 예측 근거 모달 */}
      <PredictionDetailModal detail={selectedDetail} onClose={handleCloseModal} />

      {/* 로컬 오류 메시지 (네트워크 오류 등) */}
      {localError && (
        <Alert
          {...createErrorAlert(localError, isRetryableError(localError))}
          onClose={() => setLocalError(null)}
          onRetry={isRetryableError(localError) ? handleRetry : undefined}
        />
      )}

      {/* 종목 검색 */}
      <div className="bg-white rounded-lg shadow p-6">
        <StockSearch />
        
        {/* 예측 버튼 */}
        <div className="mt-6">
          <button
            onClick={handlePredict}
            disabled={!selectedStock || loading}
            className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-all ${
              !selectedStock || loading
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                예측 생성 중...
              </span>
            ) : (
              'AI 예측 실행'
            )}
          </button>
        </div>
      </div>

      {/* 로딩 상태 */}
      {loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <svg
              className="animate-spin h-6 w-6 text-blue-600"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <div>
              <div className="font-medium text-blue-900">예측 생성 중</div>
              <div className="text-sm text-blue-700">
                5개의 AI 모델이 분석하고 있습니다. 잠시만 기다려주세요...
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 예측 결과 테이블 */}
      {predictions && !loading && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-4 md:px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg md:text-xl font-bold text-gray-900">예측 결과</h2>
            <div className="mt-2 text-xs md:text-sm text-gray-600">
              <span className="font-medium">{predictions.name}</span>
              <span className="mx-2">•</span>
              <span>현재가: {predictions.currentPrice?.toLocaleString()}원</span>
              <span className="mx-2 hidden sm:inline">•</span>
              <span className="text-xs text-gray-500 block sm:inline mt-1 sm:mt-0">
                {new Date(predictions.timestamp).toLocaleString('ko-KR')}
              </span>
            </div>
          </div>

          {/* 데스크톱 테이블 (768px 이상) */}
          <div className="hidden md:block overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-20">
                    모델
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    1일 후
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    1주일 후
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    1개월 후
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {/* 모델별 예측 */}
                {Object.entries(predictions.predictions).map(([modelName, modelPrediction]) => (
                  <tr key={modelName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap sticky left-0 bg-white z-10">
                      <div className="text-sm font-medium text-gray-900">{modelName}</div>
                    </td>
                    {['1d', '1w', '1m'].map((period) => {
                      const pred = modelPrediction[period as keyof typeof modelPrediction];
                      if (!pred) return <td key={period} className="px-6 py-4">-</td>;
                      
                      return (
                        <td
                          key={period}
                          className="px-6 py-4 cursor-pointer hover:bg-blue-50 transition-colors"
                          onClick={() => handleShowDetail(modelName, period, pred.price, pred.reason, pred.sentiment)}
                          title="클릭하여 상세 근거 보기"
                        >
                          <div className="text-sm">
                            <div className="font-medium text-gray-900">
                              {pred.price.toLocaleString()}원
                            </div>
                            <div className="flex items-center mt-1">
                              {pred.sentiment === '긍정' ? (
                                <span className="inline-flex items-center text-xs text-green-700">
                                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                                  </svg>
                                  긍정
                                </span>
                              ) : (
                                <span className="inline-flex items-center text-xs text-red-700">
                                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                                  </svg>
                                  부정
                                </span>
                              )}
                            </div>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}

                {/* 종합 예측 */}
                <tr className="bg-blue-50 font-bold">
                  <td className="px-6 py-4 whitespace-nowrap sticky left-0 bg-blue-50 z-10">
                    <div className="text-sm font-bold text-blue-900">종합 예측</div>
                  </td>
                  {['1d', '1w', '1m'].map((period) => {
                    const ensemble = predictions.ensemble[period as keyof typeof predictions.ensemble];
                    if (!ensemble) return <td key={period} className="px-6 py-4">-</td>;
                    
                    return (
                      <td
                        key={period}
                        className={`px-6 py-4 cursor-pointer hover:bg-blue-100 transition-colors ${
                          ensemble.disagreement ? 'bg-yellow-100' : ''
                        }`}
                        onClick={() => handleShowDetail('종합 예측', period, ensemble.price, ensemble.reason, ensemble.sentiment)}
                        title="클릭하여 상세 근거 보기"
                      >
                        <div className="text-sm">
                          <div className="font-bold text-blue-900">
                            {ensemble.price.toLocaleString()}원
                          </div>
                          <div className="flex items-center mt-1">
                            {ensemble.sentiment === '긍정' ? (
                              <span className="inline-flex items-center text-xs text-green-700 font-medium">
                                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                                </svg>
                                긍정
                              </span>
                            ) : (
                              <span className="inline-flex items-center text-xs text-red-700 font-medium">
                                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                                </svg>
                                부정
                              </span>
                            )}
                          </div>
                          {ensemble.disagreement && (
                            <div className="text-xs text-yellow-700 mt-1">
                              ⚠️ 의견 불일치
                            </div>
                          )}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              </tbody>
            </table>
          </div>

          {/* 모바일 카드 뷰 (768px 미만) */}
          <div className="md:hidden divide-y divide-gray-200">
            {/* 모델별 예측 카드 */}
            {Object.entries(predictions.predictions).map(([modelName, modelPrediction]) => (
              <div key={modelName} className="p-4">
                <div className="font-semibold text-gray-900 mb-3">{modelName}</div>
                <div className="space-y-3">
                  {['1d', '1w', '1m'].map((period) => {
                    const pred = modelPrediction[period as keyof typeof modelPrediction];
                    if (!pred) return null;
                    
                    const periodLabel = period === '1d' ? '1일 후' : period === '1w' ? '1주일 후' : '1개월 후';
                    
                    return (
                      <div
                        key={period}
                        className="bg-gray-50 rounded-lg p-3 cursor-pointer hover:bg-blue-50 transition-colors"
                        onClick={() => handleShowDetail(modelName, period, pred.price, pred.reason, pred.sentiment)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-xs font-medium text-gray-600">{periodLabel}</span>
                          {pred.sentiment === '긍정' ? (
                            <span className="inline-flex items-center text-xs text-green-700">
                              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                              </svg>
                              긍정
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs text-red-700">
                              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                              </svg>
                              부정
                            </span>
                          )}
                        </div>
                        <div className="text-base font-semibold text-gray-900">
                          {pred.price.toLocaleString()}원
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          탭하여 상세 근거 보기
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* 종합 예측 카드 */}
            <div className="p-4 bg-blue-50">
              <div className="font-bold text-blue-900 mb-3">종합 예측</div>
              <div className="space-y-3">
                {['1d', '1w', '1m'].map((period) => {
                  const ensemble = predictions.ensemble[period as keyof typeof predictions.ensemble];
                  if (!ensemble) return null;
                  
                  const periodLabel = period === '1d' ? '1일 후' : period === '1w' ? '1주일 후' : '1개월 후';
                  
                  return (
                    <div
                      key={period}
                      className={`rounded-lg p-3 cursor-pointer hover:bg-blue-100 transition-colors ${
                        ensemble.disagreement ? 'bg-yellow-100' : 'bg-white'
                      }`}
                      onClick={() => handleShowDetail('종합 예측', period, ensemble.price, ensemble.reason, ensemble.sentiment)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-xs font-medium text-gray-600">{periodLabel}</span>
                        <div className="flex items-center space-x-2">
                          {ensemble.sentiment === '긍정' ? (
                            <span className="inline-flex items-center text-xs text-green-700 font-medium">
                              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                              </svg>
                              긍정
                            </span>
                          ) : (
                            <span className="inline-flex items-center text-xs text-red-700 font-medium">
                              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clipRule="evenodd" />
                              </svg>
                              부정
                            </span>
                          )}
                          {ensemble.disagreement && (
                            <span className="text-xs text-yellow-700">⚠️</span>
                          )}
                        </div>
                      </div>
                      <div className="text-base font-bold text-blue-900">
                        {ensemble.price.toLocaleString()}원
                      </div>
                      {ensemble.disagreement && (
                        <div className="text-xs text-yellow-700 mt-1">
                          모델 간 의견 불일치
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">
                        탭하여 상세 근거 보기
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* 범례 */}
          <div className="px-4 md:px-6 py-4 bg-gray-50 border-t border-gray-200">
            <div className="text-xs text-gray-600 space-y-1">
              <div>• 종합 예측은 모든 AI 모델의 평균값입니다.</div>
              <div className="hidden md:block">• 노란색 배경은 모델 간 의견 불일치를 나타냅니다 (표준편차 &gt; 평균의 20%).</div>
              <div className="md:hidden">• ⚠️ 표시는 모델 간 의견 불일치를 나타냅니다.</div>
              <div className="hidden md:block">• 각 셀을 클릭하면 상세한 예측 근거를 확인할 수 있습니다.</div>
              <div className="md:hidden">• 각 카드를 탭하면 상세한 예측 근거를 확인할 수 있습니다.</div>
            </div>
          </div>
        </div>
      )}

      {/* 초기 상태 안내 */}
      {!predictions && !loading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">예측 결과가 없습니다</h3>
          <p className="mt-2 text-sm text-gray-500">
            종목을 선택하고 'AI 예측 실행' 버튼을 클릭하여 예측을 시작하세요.
          </p>
        </div>
      )}
    </div>
  );
};
