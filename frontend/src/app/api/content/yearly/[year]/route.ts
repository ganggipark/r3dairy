import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { year: string } }
) {
  const { year } = params
  const searchParams = request.nextUrl.searchParams
  const role = searchParams.get('role')
  const token = request.headers.get('Authorization')
  const queryString = role ? `?role=${role}` : ''

  try {
    const response = await fetch(
      `${BACKEND_URL}/api/content/yearly/${year}${queryString}`,
      { method: 'GET', headers: { 'Authorization': token || '' } }
    )
    const data = await response.json()

    // Transform monthly_signals Korean keys to English keys
    if (data.content && data.content.monthly_signals) {
      const transformed: Record<number, { month: number; theme: string; energy: number }> = {}
      for (const [key, signal] of Object.entries(data.content.monthly_signals)) {
        const s = signal as any
        transformed[Number(key)] = {
          month: s['월'] ?? s.month ?? Number(key),
          theme: s['테마'] ?? s.theme ?? '',
          energy: s['에너지'] ?? s.energy ?? 3,
        }
      }
      data.content.monthly_signals = transformed
    }

    return NextResponse.json(data, { status: response.status })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}
