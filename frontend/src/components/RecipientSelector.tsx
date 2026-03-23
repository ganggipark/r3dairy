'use client'

import { useState, useEffect } from 'react'
import type { Recipient } from '@/types/recipient'
import { recipients as recipientsApi } from '@/lib/api'

interface RecipientSelectorProps {
  value: string | null          // 선택된 recipient_id (null = 내 프로필)
  onChange: (id: string | null) => void
  className?: string
}

export default function RecipientSelector({ value, onChange, className = '' }: RecipientSelectorProps) {
  const [list, setList] = useState<Recipient[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (!token) { setLoading(false); return }

    recipientsApi.list(token)
      .then(setList)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return null
  if (list.length === 0) return null

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <label className="text-sm text-gray-600 whitespace-nowrap">대상자</label>
      <select
        value={value ?? ''}
        onChange={e => onChange(e.target.value || null)}
        className="text-sm border border-gray-300 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-blue-400"
      >
        <option value="">내 프로필</option>
        {list.map(r => (
          <option key={r.id} value={r.id}>
            {r.name} {r.is_default ? '(기본)' : ''}
          </option>
        ))}
      </select>
    </div>
  )
}
