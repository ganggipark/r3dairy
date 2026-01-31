import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  const token = request.headers.get('Authorization')

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
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

export async function POST(request: NextRequest) {
  const token = request.headers.get('Authorization')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token || '',
      },
      body,
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

export async function PUT(request: NextRequest) {
  const token = request.headers.get('Authorization')
  const body = await request.text()

  try {
    const response = await fetch(`${BACKEND_URL}/api/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token || '',
      },
      body,
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
