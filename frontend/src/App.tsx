import { useEffect, useState } from 'react'
import { useAppStore } from './store/useAppStore'
import { useHealthCheck } from './hooks/useApi'
import { RankingTab } from './components/RankingTab'
import { PredictionTab } from './components/PredictionTab'
import { Alert, createErrorAlert } from './components/Alert'

function App() {
  const { error, clearError } = useAppStore();
  const { checkHealth, data: healthData } = useHealthCheck();
  const [activeTab, setActiveTab] = useState<'ranking' | 'prediction'>('ranking');

  useEffect(() => {
    // 앱 시작 시 서버 상태 확인
    checkHealth().catch(console.error);
  }, []);

  // 오류 재시도 핸들러
  const handleRetry = () => {
    clearError();
    // 현재 탭에 따라 적절한 재시도 로직 실행
    if (activeTab === 'ranking') {
      // 순위 데이터 재조회는 RankingTab에서 자동으로 처리됨
      window.location.reload();
    } else {
      // 예측 탭의 경우 사용자가 다시 예측 버튼을 클릭해야 함
      clearError();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 md:py-6 px-4">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            다중 AI 주식 예측 시스템
          </h1>
          {healthData && (
            <p className="text-xs md:text-sm text-gray-500 mt-2">
              서버 상태: {healthData.status}
            </p>
          )}
        </div>
      </header>

      {/* 탭 네비게이션 */}
      <div className="max-w-7xl mx-auto px-4 mt-4 md:mt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-4 md:space-x-8">
            <button
              onClick={() => setActiveTab('ranking')}
              className={`${
                activeTab === 'ranking'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              거래대금 순위
            </button>
            <button
              onClick={() => setActiveTab('prediction')}
              className={`${
                activeTab === 'prediction'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-3 md:py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
            >
              종목 예측
            </button>
          </nav>
        </div>
      </div>

      <main className="max-w-7xl mx-auto py-4 md:py-6 px-4">
        {/* 전역 오류 메시지 */}
        {error && (
          <div className="mb-4 md:mb-6">
            <Alert
              {...createErrorAlert(new Error(error), true)}
              onClose={clearError}
              onRetry={handleRetry}
            />
          </div>
        )}

        {/* 탭 컨텐츠 */}
        {activeTab === 'ranking' && <RankingTab />}
        {activeTab === 'prediction' && <PredictionTab />}
      </main>
    </div>
  )
}

export default App
