'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { Recipient, RecipientCreate } from '@/types/recipient'
import { recipients as recipientsApi } from '@/lib/api'

const GENDER_LABELS: Record<string, string> = {
  male: '남성', female: '여성', other: '기타'
}
const ROLE_LABELS: Record<string, string> = {
  student: '학생', office_worker: '직장인', freelancer: '프리랜서/자영업'
}

const emptyForm: RecipientCreate = {
  name: '',
  birth_date: '',
  birth_time: '00:00:00',
  gender: 'male',
  birth_place: '',
  role: 'office_worker',
  relationship: '',
  is_default: false,
}

export default function RecipientsPage() {
  const router = useRouter()
  const [list, setList] = useState<Recipient[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editTarget, setEditTarget] = useState<Recipient | null>(null)
  const [form, setForm] = useState<RecipientCreate>(emptyForm)
  const [saving, setSaving] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    loadList()
  }, [])

  async function loadList() {
    const token = localStorage.getItem('access_token')
    if (!token) return
    setLoading(true)
    try {
      const data = await recipientsApi.list(token)
      setList(data)
    } catch {
      setError('대상자 목록을 불러오지 못했습니다.')
    } finally {
      setLoading(false)
    }
  }

  function openAdd() {
    setEditTarget(null)
    setForm(emptyForm)
    setShowForm(true)
  }

  function openEdit(r: Recipient) {
    setEditTarget(r)
    setForm({
      name: r.name,
      birth_date: r.birth_date,
      birth_time: r.birth_time,
      gender: r.gender,
      birth_place: r.birth_place,
      role: r.role,
      relationship: r.relationship ?? '',
      is_default: r.is_default,
    })
    setShowForm(true)
  }

  async function handleSave() {
    if (!form.name || !form.birth_date || !form.gender) {
      setError('이름, 생년월일, 성별은 필수입니다.')
      return
    }
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    setSaving(true)
    setError('')
    try {
      if (editTarget) {
        await recipientsApi.update(token, editTarget.id, form)
      } else {
        await recipientsApi.create(token, form)
      }
      setShowForm(false)
      await loadList()
    } catch {
      setError('저장에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(id: string) {
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    try {
      await recipientsApi.delete(token, id)
      setDeleteId(null)
      await loadList()
    } catch {
      setError('삭제에 실패했습니다.')
    }
  }

  async function handleSetDefault(id: string) {
    const token = localStorage.getItem('access_token')
    if (!token) { router.push('/login'); return }
    try {
      await recipientsApi.setDefault(token, id)
      await loadList()
    } catch {
      setError('기본 설정에 실패했습니다.')
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">다이어리 대상자</h1>
        <button
          onClick={openAdd}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
        >
          + 대상자 추가
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded text-sm">{error}</div>
      )}

      {loading ? (
        <div className="text-center text-gray-500 py-12">불러오는 중...</div>
      ) : list.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          <p className="mb-2">등록된 대상자가 없습니다.</p>
          <p className="text-sm">위 버튼으로 대상자를 추가하세요.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {list.map(r => (
            <div key={r.id} className="border rounded-lg p-4 bg-white shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{r.name}</span>
                    {r.is_default && (
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">기본</span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {r.birth_date} {r.birth_time?.slice(0, 5)} · {GENDER_LABELS[r.gender] ?? r.gender} · {ROLE_LABELS[r.role] ?? r.role}
                  </div>
                  {r.birth_place && <div className="text-sm text-gray-400">{r.birth_place}</div>}
                </div>
                <div className="flex gap-2 text-sm">
                  {!r.is_default && (
                    <button onClick={() => handleSetDefault(r.id)} className="text-blue-500 hover:underline">기본 설정</button>
                  )}
                  <button onClick={() => openEdit(r)} className="text-gray-500 hover:underline">수정</button>
                  <button onClick={() => setDeleteId(r.id)} className="text-red-400 hover:underline">삭제</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold mb-4">{editTarget ? '대상자 수정' : '대상자 추가'}</h2>
            {error && <div className="mb-3 text-red-600 text-sm">{error}</div>}
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">이름 *</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                  placeholder="홍길동"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium mb-1">생년월일 *</label>
                  <input
                    type="date"
                    value={form.birth_date}
                    onChange={e => setForm(f => ({ ...f, birth_date: e.target.value }))}
                    className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">태어난 시각</label>
                  <input
                    type="time"
                    value={form.birth_time?.slice(0, 5)}
                    onChange={e => setForm(f => ({ ...f, birth_time: e.target.value + ':00' }))}
                    className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">성별 *</label>
                <select
                  value={form.gender}
                  onChange={e => setForm(f => ({ ...f, gender: e.target.value as 'male' | 'female' | 'other' }))}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                >
                  <option value="male">남성</option>
                  <option value="female">여성</option>
                  <option value="other">기타</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">출생지</label>
                <input
                  type="text"
                  value={form.birth_place}
                  onChange={e => setForm(f => ({ ...f, birth_place: e.target.value }))}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                  placeholder="서울"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">역할</label>
                <select
                  value={form.role}
                  onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
                  className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
                >
                  <option value="student">학생</option>
                  <option value="office_worker">직장인</option>
                  <option value="freelancer">프리랜서/자영업</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_default"
                  checked={form.is_default}
                  onChange={e => setForm(f => ({ ...f, is_default: e.target.checked }))}
                />
                <label htmlFor="is_default" className="text-sm">기본 대상자로 설정</label>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-5">
              <button
                onClick={() => { setShowForm(false); setError('') }}
                className="px-4 py-2 text-sm border rounded hover:bg-gray-50"
              >취소</button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >{saving ? '저장 중...' : '저장'}</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteId && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full">
            <h3 className="font-bold mb-2">대상자 삭제</h3>
            <p className="text-sm text-gray-600 mb-4">정말 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.</p>
            <div className="flex justify-end gap-3">
              <button onClick={() => setDeleteId(null)} className="px-4 py-2 text-sm border rounded hover:bg-gray-50">취소</button>
              <button onClick={() => handleDelete(deleteId)} className="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700">삭제</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
