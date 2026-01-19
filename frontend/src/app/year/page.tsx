'use client'

/**
 * Year Page
 * 연간 콘텐츠 페이지
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { YearlyContentResponse, Role } from '@/types'

export default function YearPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [yearlyContent, setYearlyContent] = useState<YearlyContentResponse | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [userRoles, setUserRoles] = useState<Role[]>([])

  // 현재 년도
  const currentYear = new Date().getFullYear()

  useEffect(() => {
    const loadData = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      try {
        // 프로필에서 역할 정보 가져오기
        const profile = await api.profile.get(token)
        setUserRoles(profile.roles)
        setSelectedRole(profile.roles[0])

        // 연간 콘텐츠 로드
        const content = await api.content.getYearly(token, currentYear, profile.roles[0])
        setYearlyContent(content)
      } catch (err: any) {
        setError(err.message || '데이터를 불러오는 데 실패했습니다')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [router, currentYear])

  // 역할 변경 시 콘텐츠 다시 로드
  const handleRoleChange = async (newRole: Role) => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    setSelectedRole(newRole)
    try {
      const content = await api.content.getYearly(token, currentYear, newRole)
      setYearlyContent(content)
    } catch (err: any) {
      setError('콘텐츠를 불러오는 데 실패했습니다')
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">올해 콘텐츠를 불러오는 중...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-600">{error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">올해의 흐름</h1>
              <p className="text-sm text-gray-600">{currentYear}년</p>
            </div>

            {/* 역할 선택 */}
            {userRoles.length > 1 && (
              <div className="flex gap-2">
                {userRoles.map(role => (
                  <button
                    key={role}
                    onClick={() => handleRoleChange(role)}
                    className={`px-4 py-2 rounded-md text-sm font-medium ${
                      selectedRole === role
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {role === Role.STUDENT ? '학생' : role === Role.OFFICE_WORKER ? '직장인' : '프리랜서'}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">연간 콘텐츠</h2>

          {/* TODO: YearlyContent 타입이 정의되면 구체적인 렌더링 추가 */}
          <div className="text-gray-700">
            <p className="mb-4">연간 콘텐츠 구조는 Phase 3에서 정의될 예정입니다.</p>
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(yearlyContent, null, 2)}
            </pre>
          </div>
        </div>
      </main>
    </div>
  )
}
