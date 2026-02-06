/**
 * 거래대금 순위 탭 컴포넌트
 * 거래대금 기준 상위 종목을 테이블 형태로 표시하고 1분마다 자동 갱신
 */

import React, { useEffect, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';
import { apiService } from '../services/api';
import { MiniChart } from './MiniChart';
import { Alert, createErrorAlert } from './Alert';

/**
 * 거래대금 순위 탭 컴포넌트
 */
export const RankingTab: React.FC = () => {
  const { rankings, loading, error, setRankings, setLoading, setError } = useAppStore();

  /**
   * 순위 데이터 조회
   */
  const fetchRankings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getRankings();
      setRankings(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '순위 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      console.error('순위 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  }, [setRankings, setLoading, setError]);

  /**
   * 컴포넌트 마운트 시 데이터 조회 및 1분 간격 자동 갱신 설정
   */
  useEffect(() => {
    // 초기 데이터 로드
    fetchRankings();

    // 1분(60000ms) 간격으로 자동 갱신
    const intervalId = setInterval(() => {
      fetchRankings();
    }, 60000);

    // 컴포넌트 언마운트 시 인터벌 정리
    return () => {
      clearInterval(intervalId);
    };
  }, [fetchRankings]);

  /**
   * 등락률에 따른 색상 클래스 반환
   */
  const getChangeRateColor = (changeRate: number): string => {
    if (changeRate > 0) return 'text-red-600';
    if (changeRate < 0) return 'text-blue-600';
    return 'text-gray-600';
  };

  /**
   * 등락률 포맷팅 (부호 포함)
   */
  const formatChangeRate = (changeRate: number): string => {
    const sign = changeRate > 0 ? '+' : '';
    return `${sign}${changeRate.toFixed(2)}%`;
  };

  /**
   * 숫자를 천 단위 구분 기호로 포맷팅
   */
  const formatNumber = (num: number): string => {
    return num.toLocaleString('ko-KR');
  };

  /**
   * 로딩 상태 렌더링
   */
  if (loading && rankings.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-4">거래대금 순위를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  /**
   * 오류 상태 렌더링
   */
  if (error && rankings.length === 0) {
    return (
      <Alert
        {...createErrorAlert(new Error(error), true)}
        onRetry={fetchRankings}
        onClose={() => setError(null)}
      />
    );
  }

  /**
   * 순위 테이블 렌더링
   */
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* 헤더 */}
      <div className="px-4 md:px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg md:text-xl font-semibold text-gray-900">거래대금 순위</h2>
        <div className="flex items-center space-x-2">
          {loading && (
            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          <span className="text-xs md:text-sm text-gray-500 hidden sm:inline">1분마다 자동 갱신</span>
        </div>
      </div>

      {/* 데스크톱 테이블 (768px 이상) */}
      <div className="hidden md:block overflow-x-auto max-h-[600px] overflow-y-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-20">
                순위
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                종목명
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                종목코드
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                현재가
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                등락률
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                거래대금
              </th>
              <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                추이
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {rankings.map((stock) => (
              <tr key={stock.symbol} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white z-10">
                  {stock.rank}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {stock.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {stock.symbol}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  {formatNumber(stock.currentPrice)}원
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${getChangeRateColor(stock.changeRate)}`}>
                  {formatChangeRate(stock.changeRate)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                  {formatNumber(stock.tradingValue)}억원
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  {stock.miniChartData && stock.miniChartData.length > 0 ? (
                    <MiniChart
                      data={stock.miniChartData}
                      width={100}
                      height={30}
                      color={stock.changeRate >= 0 ? '#dc2626' : '#2563eb'}
                    />
                  ) : (
                    <span className="text-xs text-gray-400">데이터 없음</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 모바일 카드 뷰 (768px 미만) */}
      <div className="md:hidden divide-y divide-gray-200">
        {rankings.map((stock) => (
          <div key={stock.symbol} className="p-4 hover:bg-gray-50 transition-colors">
            {/* 순위와 종목명 */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold text-blue-600">{stock.rank}</span>
                </div>
                <div>
                  <div className="text-base font-semibold text-gray-900">{stock.name}</div>
                  <div className="text-xs text-gray-500">{stock.symbol}</div>
                </div>
              </div>
            </div>

            {/* 가격 정보 */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div>
                <div className="text-xs text-gray-500 mb-1">현재가</div>
                <div className="text-sm font-medium text-gray-900">
                  {formatNumber(stock.currentPrice)}원
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500 mb-1">등락률</div>
                <div className={`text-sm font-bold ${getChangeRateColor(stock.changeRate)}`}>
                  {formatChangeRate(stock.changeRate)}
                </div>
              </div>
            </div>

            {/* 거래대금 */}
            <div className="mb-3">
              <div className="text-xs text-gray-500 mb-1">거래대금</div>
              <div className="text-sm font-medium text-gray-900">
                {formatNumber(stock.tradingValue)}억원
              </div>
            </div>

            {/* 미니 차트 */}
            {stock.miniChartData && stock.miniChartData.length > 0 && (
              <div className="pt-3 border-t border-gray-100">
                <div className="text-xs text-gray-500 mb-2">최근 추이</div>
                <MiniChart
                  data={stock.miniChartData}
                  width={200}
                  height={40}
                  color={stock.changeRate >= 0 ? '#dc2626' : '#2563eb'}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 데이터가 없을 때 */}
      {rankings.length === 0 && !loading && !error && (
        <div className="text-center py-12">
          <p className="text-gray-500">표시할 순위 데이터가 없습니다.</p>
        </div>
      )}
    </div>
  );
};
