import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    version: '0.2.0',
    environment: process.env.NODE_ENV || 'development',
  })
}
