'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  CalendarDays,
  CalendarRange,
  Calendar,
  Users,
  Printer,
  User,
  Settings,
} from 'lucide-react'

const NAV_ITEMS = [
  { href: '/today', label: '오늘', icon: CalendarDays },
  { href: '/month', label: '월간', icon: CalendarRange },
  { href: '/year', label: '연간', icon: Calendar },
  { href: '/recipients', label: '대상자', icon: Users },
  { href: '/diary-print', label: '인쇄', icon: Printer },
  { href: '/profile', label: '프로필', icon: User },
  { href: '/settings', label: '설정', icon: Settings },
]

export default function NavBar() {
  const pathname = usePathname()

  const isActive = (href: string) =>
    pathname === href || pathname.startsWith(href + '/')

  return (
    <>
      {/* 데스크톱: 상단 수평 네비게이션 (md 이상) */}
      <nav className="hidden md:flex sticky top-0 z-50 w-full bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center w-full px-4 h-14">
          <span className="text-lg font-bold text-gray-800 mr-8 whitespace-nowrap">R³ Diary</span>
          <ul className="flex items-center gap-1">
            {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
              <li key={href}>
                <Link
                  href={href}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(href)
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      {/* 모바일: 하단 고정 탭 바 (md 미만) */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
        <ul className="flex items-center justify-around h-16">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
            <li key={href} className="flex-1">
              <Link
                href={href}
                className={`flex flex-col items-center justify-center gap-0.5 h-16 text-xs font-medium transition-colors ${
                  isActive(href)
                    ? 'text-blue-600'
                    : 'text-gray-500 hover:text-gray-900'
                }`}
              >
                <Icon size={20} />
                <span>{label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* 모바일 하단 바 높이만큼 패딩 확보 */}
      <div className="md:hidden h-16" />
    </>
  )
}
