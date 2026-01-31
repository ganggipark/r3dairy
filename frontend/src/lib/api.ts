/**
 * API Client
 * Backend API 호출을 위한 클라이언트
 */

import type {
  AuthResponse,
  SignUpRequest,
  LoginRequest,
  Profile,
  ProfileCreate,
  ProfileUpdate,
  DailyContentResponse,
  DailyMarkdownResponse,
  MonthlyContentResponse,
  YearlyContentResponse,
  DailyLog,
  DailyLogCreate,
  DailyLogUpdate,
  SuccessResponse,
  Role
} from '@/types'

// Use empty string to make same-origin requests through Next.js API Route proxy
// This solves CORS issues by routing all requests through /api/* routes
const API_URL = ''

/**
 * API 에러 처리
 */
class APIError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: string
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Fetch 래퍼 (에러 처리 포함)
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'Unknown error',
      message: response.statusText
    }))

    // FastAPI는 detail 필드를 사용, 기존 error/message 필드도 지원
    const errorMessage = error.detail || error.error || error.message || 'API Error'

    throw new APIError(
      response.status,
      errorMessage,
      error.details
    )
  }

  return response.json()
}

// ============================================================================
// Auth API
// ============================================================================

export const auth = {
  /**
   * 회원가입
   */
  signUp: async (data: SignUpRequest): Promise<AuthResponse> => {
    return fetchAPI<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  /**
   * 로그인
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    return fetchAPI<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },

  /**
   * 로그아웃
   */
  logout: async (token: string): Promise<SuccessResponse> => {
    return fetchAPI<SuccessResponse>('/api/auth/logout', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  },

  /**
   * 토큰 갱신
   */
  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    return fetchAPI<AuthResponse>('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    })
  },

  /**
   * 비밀번호 변경
   */
  changePassword: async (
    token: string,
    currentPassword: string,
    newPassword: string
  ): Promise<SuccessResponse> => {
    return fetchAPI<SuccessResponse>('/api/auth/change-password', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    })
  }
}

// ============================================================================
// Profile API
// ============================================================================

export const profile = {
  /**
   * 프로필 생성
   */
  create: async (token: string, data: ProfileCreate): Promise<Profile> => {
    return fetchAPI<Profile>('/api/profile', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
  },

  /**
   * 프로필 조회
   */
  get: async (token: string): Promise<Profile> => {
    return fetchAPI<Profile>('/api/profile', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  },

  /**
   * 프로필 수정
   */
  update: async (
    token: string,
    data: ProfileUpdate
  ): Promise<Profile> => {
    return fetchAPI<Profile>('/api/profile', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
  },

  /**
   * 프로필 삭제
   */
  delete: async (token: string): Promise<SuccessResponse> => {
    return fetchAPI<SuccessResponse>('/api/profile', {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  }
}

// ============================================================================
// Daily Content API
// ============================================================================

export const daily = {
  /**
   * 일간 콘텐츠 조회
   */
  getContent: async (
    token: string,
    date: string,
    role?: Role
  ): Promise<DailyContentResponse> => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)

    return fetchAPI<DailyContentResponse>(
      `/api/daily/${date}${params.toString() ? `?${params.toString()}` : ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
  },

  /**
   * 일간 콘텐츠 Markdown 조회
   */
  getMarkdown: async (
    token: string,
    date: string,
    role?: Role
  ): Promise<DailyMarkdownResponse> => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)

    return fetchAPI<DailyMarkdownResponse>(
      `/api/daily/${date}/markdown${params.toString() ? `?${params.toString()}` : ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
  },

  /**
   * 기간별 일간 콘텐츠 조회 (최대 31일)
   */
  getContentRange: async (
    token: string,
    startDate: string,
    endDate: string,
    role?: Role
  ): Promise<DailyContentResponse[]> => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)

    return fetchAPI<DailyContentResponse[]>(
      `/api/daily/range/${startDate}/${endDate}${params.toString() ? `?${params.toString()}` : ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
  }
}

// ============================================================================
// Monthly/Yearly Content API
// ============================================================================

export const content = {
  /**
   * 월간 콘텐츠 조회
   */
  getMonthly: async (
    token: string,
    year: number,
    month: number,
    role?: Role
  ): Promise<MonthlyContentResponse> => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)

    return fetchAPI<MonthlyContentResponse>(
      `/api/content/monthly/${year}/${month}${params.toString() ? `?${params.toString()}` : ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
  },

  /**
   * 연간 콘텐츠 조회
   */
  getYearly: async (
    token: string,
    year: number,
    role?: Role
  ): Promise<YearlyContentResponse> => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)

    return fetchAPI<YearlyContentResponse>(
      `/api/content/yearly/${year}${params.toString() ? `?${params.toString()}` : ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
  }
}

// ============================================================================
// Daily Log API
// ============================================================================

export const logs = {
  /**
   * 일간 기록 생성
   */
  create: async (
    token: string,
    date: string,
    data: DailyLogCreate
  ): Promise<DailyLog> => {
    return fetchAPI<DailyLog>(`/api/logs/${date}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
  },

  /**
   * 일간 기록 조회
   */
  get: async (token: string, date: string): Promise<DailyLog> => {
    return fetchAPI<DailyLog>(`/api/logs/${date}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  },

  /**
   * 일간 기록 수정
   */
  update: async (
    token: string,
    date: string,
    data: DailyLogUpdate
  ): Promise<DailyLog> => {
    return fetchAPI<DailyLog>(`/api/logs/${date}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(data)
    })
  },

  /**
   * 일간 기록 삭제
   */
  delete: async (token: string, date: string): Promise<SuccessResponse> => {
    return fetchAPI<SuccessResponse>(`/api/logs/${date}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  }
}

// ============================================================================
// Export
// ============================================================================

export const api = {
  auth,
  profile,
  daily,
  content,
  logs
}

export { APIError }
