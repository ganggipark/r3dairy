'use client'

/**
 * Profile Page
 * 프로필 생성/수정 페이지
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { Profile, ProfileCreate, ProfileUpdate } from '@/types'
import { Gender, Role } from '@/types'

export default function ProfilePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [isEditMode, setIsEditMode] = useState(false)
  const [existingProfile, setExistingProfile] = useState<Profile | null>(null)

  const [formData, setFormData] = useState({
    name: '',
    birth_date: '',
    birth_time: '',
    gender: '' as Gender | '',
    birth_place: '',
    roles: [] as Role[],
    preferences: {}
  })

  // 기존 프로필 로드
  useEffect(() => {
    const loadProfile = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/login')
        return
      }

      try {
        const profile = await api.profile.get(token)
        setExistingProfile(profile)
        setIsEditMode(true)
        setFormData({
          name: profile.name,
          birth_date: profile.birth_date,
          birth_time: profile.birth_time,
          gender: profile.gender,
          birth_place: profile.birth_place,
          roles: profile.roles,
          preferences: profile.preferences || {}
        })
      } catch (err: any) {
        // 프로필이 없으면 프로필 생성 페이지로
        if (err.status === 404) {
          router.push('/profile')
          return
        } else {
          setError('프로필을 불러오는 데 실패했습니다')
        }
      } finally {
        setIsLoading(false)
      }
    }

    loadProfile()
  }, [router])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleRoleToggle = (role: Role) => {
    const currentRoles = formData.roles
    if (currentRoles.includes(role)) {
      setFormData({
        ...formData,
        roles: currentRoles.filter(r => r !== role)
      })
    } else {
      setFormData({
        ...formData,
        roles: [...currentRoles, role]
      })
    }
  }

  const validateForm = (): boolean => {
    if (!formData.name || !formData.birth_date || !formData.birth_time ||
        !formData.gender || !formData.birth_place) {
      setError('모든 필수 필드를 입력해주세요')
      return false
    }

    if (formData.roles.length === 0) {
      setError('최소 1개 이상의 역할을 선택해주세요')
      return false
    }

    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!validateForm()) {
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }

    setIsSaving(true)

    try {
      if (isEditMode) {
        // 프로필 수정
        const updateData: ProfileUpdate = {
          name: formData.name,
          birth_date: formData.birth_date,
          birth_time: formData.birth_time,
          gender: formData.gender as Gender,
          birth_place: formData.birth_place,
          roles: formData.roles,
          preferences: formData.preferences
        }
        await api.profile.update(token, updateData)
      } else {
        // 프로필 생성
        const createData: ProfileCreate = {
          name: formData.name,
          birth_date: formData.birth_date,
          birth_time: formData.birth_time,
          gender: formData.gender as Gender,
          birth_place: formData.birth_place,
          roles: formData.roles,
          preferences: formData.preferences
        }
        await api.profile.create(token, createData)
      }

      // 오늘 페이지로 이동
      router.push('/today')
    } catch (err: any) {
      setError(err.message || '프로필 저장에 실패했습니다')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">프로필을 불러오는 중...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              {isEditMode ? '프로필 수정' : '프로필 생성'}
            </h2>
            <p className="mt-1 text-sm text-gray-600">
              정확한 출생 정보를 입력해주세요. 이 정보를 바탕으로 나만의 리듬을 분석합니다.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 이름 */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                이름 *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                disabled={isSaving}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* 생년월일 */}
            <div>
              <label htmlFor="birth_date" className="block text-sm font-medium text-gray-700">
                생년월일 *
              </label>
              <input
                type="date"
                id="birth_date"
                name="birth_date"
                required
                value={formData.birth_date}
                onChange={handleChange}
                disabled={isSaving}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* 출생 시간 */}
            <div>
              <label htmlFor="birth_time" className="block text-sm font-medium text-gray-700">
                출생 시간 *
              </label>
              <input
                type="time"
                id="birth_time"
                name="birth_time"
                required
                value={formData.birth_time}
                onChange={handleChange}
                disabled={isSaving}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-500">
                정확한 출생 시간을 모르는 경우 추정 시간을 입력해주세요
              </p>
            </div>

            {/* 성별 */}
            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-gray-700">
                성별 *
              </label>
              <select
                id="gender"
                name="gender"
                required
                value={formData.gender}
                onChange={handleChange}
                disabled={isSaving}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="">선택해주세요</option>
                <option value="male">남성</option>
                <option value="female">여성</option>
              </select>
            </div>

            {/* 출생 장소 */}
            <div>
              <label htmlFor="birth_place" className="block text-sm font-medium text-gray-700">
                출생 장소 *
              </label>
              <input
                type="text"
                id="birth_place"
                name="birth_place"
                required
                value={formData.birth_place}
                onChange={handleChange}
                disabled={isSaving}
                placeholder="예: 서울특별시"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* 역할 선택 (다중 선택) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                역할 선택 * (여러 개 선택 가능)
              </label>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.roles.includes(Role.STUDENT)}
                    onChange={() => handleRoleToggle(Role.STUDENT)}
                    disabled={isSaving}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">학생</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.roles.includes(Role.OFFICE_WORKER)}
                    onChange={() => handleRoleToggle(Role.OFFICE_WORKER)}
                    disabled={isSaving}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">직장인</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.roles.includes(Role.FREELANCER)}
                    onChange={() => handleRoleToggle(Role.FREELANCER)}
                    disabled={isSaving}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">프리랜서</span>
                </label>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                선택한 역할에 맞는 표현으로 일간 콘텐츠가 제공됩니다
              </p>
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}

            {/* 제출 버튼 */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isSaving}
                className="flex-1 py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
              >
                {isSaving ? '저장 중...' : (isEditMode ? '수정 완료' : '프로필 생성')}
              </button>
              {isEditMode && (
                <button
                  type="button"
                  onClick={() => router.push('/today')}
                  className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  취소
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
