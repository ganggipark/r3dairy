import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(
  request: NextRequest,
  { params }: { params: { date: string } }
) {
  const { date } = params
  const searchParams = request.nextUrl.searchParams
  const role = searchParams.get('role')
  const token = request.headers.get('Authorization')

  const queryString = role ? `?role=${role}` : ''

  try {
    const response = await fetch(`${BACKEND_URL}/api/daily/${date}${queryString}`, {
      method: 'GET',
      headers: {
        'Authorization': token || '',
      },
    })

    const data = await response.json()

    return NextResponse.json(data, {
      status: response.status,
    })
  } catch (error: any) {
    return NextResponse.json(
      { detail: `Backend connection failed: ${error.message}` },
      { status: 500 }
    )
  }
}
