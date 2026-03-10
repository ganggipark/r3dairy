'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  const handleDemoMode = () => {
    // Set dummy tokens for development
    localStorage.setItem('access_token', 'demo-token-dev-mode')
    localStorage.setItem('refresh_token', 'demo-refresh-token-dev-mode')
    localStorage.setItem('user_id', 'demo-user-123')
    // Redirect to today page
    router.push('/today')
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center max-w-2xl">
        <h1 className="text-5xl font-bold mb-4 text-gray-900">R³ Diary System</h1>
        <p className="text-2xl mb-8 text-blue-600 font-semibold">Rhythm → Response → Recode</p>
        <div className="space-y-3 mb-12">
          <p className="text-lg text-gray-700">출생 정보 기반 리듬 분석과 사용자 기록을 결합한</p>
          <p className="text-lg text-gray-700">개인 맞춤 다이어리 애플리케이션</p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          {process.env.NODE_ENV === 'development' && (
            <button
              onClick={handleDemoMode}
              className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-white bg-green-600 hover:bg-green-700 rounded-lg shadow-md transition-colors duration-200"
            >
              🚀 데모 모드 (개발용)
            </button>
          )}
          <Link
            href="/login"
            className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md transition-colors duration-200"
          >
            로그인
          </Link>
          <Link
            href="/signup"
            className="w-full sm:w-auto px-8 py-3 text-lg font-semibold text-blue-600 bg-white hover:bg-gray-50 border-2 border-blue-600 rounded-lg shadow-md transition-colors duration-200"
          >
            회원가입
          </Link>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">주요 기능</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-bold text-blue-900 mb-2">일간 리듬</h3>
              <p className="text-sm text-gray-700">오늘의 흐름을 분석하고 최적의 행동 가이드를 제공합니다</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-bold text-blue-900 mb-2">월간 테마</h3>
              <p className="text-sm text-gray-700">이번 달의 전체 흐름과 중요 시기를 확인하세요</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <h3 className="font-bold text-blue-900 mb-2">개인 기록</h3>
              <p className="text-sm text-gray-700">감정, 에너지, 감사 일기를 작성하고 패턴을 파악합니다</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
