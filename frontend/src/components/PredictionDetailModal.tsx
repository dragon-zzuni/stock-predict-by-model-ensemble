/**
 * 예측 근거 상세 모달 컴포넌트
 * 
 * 클릭/호버 이벤트 처리 및 모달 표시를 담당합니다.
 * Requirements: 12.1, 12.2
 */

import { useEffect } from 'react';

interface PredictionDetail {
  modelName: string;
  period: string;
  price: number;
  reason: string;
  sentiment: string;
}

interface PredictionDetailModalProps {
  detail: PredictionDetail | null;
  onClose: () => void;
}

export const PredictionDetailModal = ({ detail, onClose }: PredictionDetailModalProps) => {
  // ESC 키로 모달 닫기
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (detail) {
      document.addEventListener('keydown', handleEscape);
      // 모달이 열릴 때 body 스크롤 방지
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [detail, onClose]);

  if (!detail) return null;

  // 기간 레이블 변환
  const getPeriodLabel = (period: string) => {
    switch (period) {
      case '1d':
        return '1일 후';
      case '1w':
        return '1주일 후';
      case '1m':
        return '1개월 후';
      default:
        return period;
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      {/* 배경 오버레이 */}
      <div
        className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        onClick={onClose}
      ></div>

      {/* 모달 컨텐츠 */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative transform overflow-hidden rounded-lg bg-white shadow-xl transition-all w-full max-w-2xl">
          {/* 헤더 */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white" id="modal-title">
                  예측 근거 상세
                </h3>
                <p className="text-sm text-blue-100 mt-1">
                  {detail.modelName} • {getPeriodLabel(detail.period)}
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors"
                aria-label="닫기"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* 본문 */}
          <div className="px-6 py-5 space-y-4">
            {/* 예측 가격 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1">예측 가격</div>
              <div className="flex items-center justify-between">
                <div className="text-2xl font-bold text-gray-900">
                  {detail.price.toLocaleString()}원
                </div>
                <div
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    detail.sentiment === '긍정'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {detail.sentiment === '긍정' ? (
                    <>
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                      긍정
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z"
                          clipRule="evenodd"
                        />
                      </svg>
                      부정
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* 예측 근거 */}
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2">예측 근거</div>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {detail.reason}
                </p>
              </div>
            </div>

            {/* 안내 메시지 */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex">
                <svg
                  className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">참고사항</p>
                  <p>
                    이 예측은 AI 모델이 제공한 분석이며, 투자 결정의 참고 자료로만 활용해야 합니다.
                    실제 투자 시에는 다양한 요소를 종합적으로 고려해주세요.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 푸터 */}
          <div className="bg-gray-50 px-6 py-4 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
