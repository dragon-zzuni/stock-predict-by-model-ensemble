/**
 * Alert 컴포넌트
 * 오류 메시지를 사용자 친화적으로 표시하고 해결 방법을 제공
 */

import { XMarkIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

export type AlertType = 'error' | 'warning' | 'info';

export interface AlertProps {
  type: AlertType;
  title: string;
  message: string;
  details?: string;
  solution?: string;
  onClose?: () => void;
  onRetry?: () => void;
  retryable?: boolean;
}

/**
 * Alert 컴포넌트
 */
export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  message,
  details,
  solution,
  onClose,
  onRetry,
  retryable = false,
}) => {
  // 타입별 스타일 설정
  const styles = {
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-600',
      title: 'text-red-800',
      message: 'text-red-700',
      button: 'bg-red-600 hover:bg-red-700 text-white',
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-600',
      title: 'text-yellow-800',
      message: 'text-yellow-700',
      button: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-600',
      title: 'text-blue-800',
      message: 'text-blue-700',
      button: 'bg-blue-600 hover:bg-blue-700 text-white',
    },
  };

  const currentStyle = styles[type];

  // 아이콘 선택
  const Icon = type === 'error' ? ExclamationTriangleIcon : InformationCircleIcon;

  return (
    <div className={`border rounded-lg p-4 ${currentStyle.container} relative`}>
      <div className="flex items-start">
        {/* 아이콘 */}
        <div className="flex-shrink-0">
          <Icon className={`h-6 w-6 ${currentStyle.icon}`} />
        </div>

        {/* 내용 */}
        <div className="ml-3 flex-1">
          {/* 제목 */}
          <h3 className={`text-sm font-medium ${currentStyle.title}`}>
            {title}
          </h3>

          {/* 메시지 */}
          <div className={`mt-2 text-sm ${currentStyle.message}`}>
            <p>{message}</p>

            {/* 상세 정보 */}
            {details && (
              <p className="mt-2 text-xs opacity-75">
                상세: {details}
              </p>
            )}

            {/* 해결 방법 */}
            {solution && (
              <div className="mt-3 p-2 bg-white bg-opacity-50 rounded">
                <p className="text-xs font-medium">해결 방법:</p>
                <p className="text-xs mt-1">{solution}</p>
              </div>
            )}
          </div>

          {/* 액션 버튼 */}
          {(retryable || onRetry) && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className={`px-4 py-2 rounded text-sm font-medium transition-colors ${currentStyle.button}`}
              >
                다시 시도
              </button>
            </div>
          )}
        </div>

        {/* 닫기 버튼 */}
        {onClose && (
          <button
            onClick={onClose}
            className={`flex-shrink-0 ml-3 ${currentStyle.icon} hover:opacity-75 transition-opacity`}
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * 오류 타입별 기본 메시지 생성 헬퍼
 */
export const createErrorAlert = (error: Error, retryable: boolean = false): Omit<AlertProps, 'onClose' | 'onRetry'> => {
  const message = error.message || '알 수 없는 오류가 발생했습니다.';

  // 네트워크 오류
  if (message.includes('네트워크') || message.includes('Network')) {
    return {
      type: 'error',
      title: '네트워크 오류',
      message: '서버에 연결할 수 없습니다.',
      details: message,
      solution: '인터넷 연결을 확인하고 다시 시도해주세요.',
      retryable: true,
    };
  }

  // 타임아웃 오류
  if (message.includes('timeout') || message.includes('시간 초과')) {
    return {
      type: 'error',
      title: '요청 시간 초과',
      message: '서버 응답 시간이 초과되었습니다.',
      details: message,
      solution: '잠시 후 다시 시도해주세요. 문제가 지속되면 관리자에게 문의하세요.',
      retryable: true,
    };
  }

  // 데이터 수집 오류
  if (message.includes('데이터 수집') || message.includes('Data collection')) {
    return {
      type: 'error',
      title: '데이터 수집 실패',
      message: '종목 데이터를 가져올 수 없습니다.',
      details: message,
      solution: '종목 코드를 확인하거나 잠시 후 다시 시도해주세요.',
      retryable: true,
    };
  }

  // AI 예측 오류
  if (message.includes('AI') || message.includes('예측')) {
    return {
      type: 'error',
      title: 'AI 예측 실패',
      message: 'AI 모델 예측 중 오류가 발생했습니다.',
      details: message,
      solution: '일부 AI 모델이 응답하지 않을 수 있습니다. 잠시 후 다시 시도해주세요.',
      retryable: true,
    };
  }

  // 일반 오류
  return {
    type: 'error',
    title: '오류 발생',
    message,
    solution: '문제가 지속되면 페이지를 새로고침하거나 관리자에게 문의하세요.',
    retryable,
  };
};
