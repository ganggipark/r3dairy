import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'R³ Diary - Rhythm, Response, Recode',
  description: 'Personalized rhythm-based diary system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
