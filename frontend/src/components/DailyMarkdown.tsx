'use client'

/**
 * DailyMarkdown Component
 *
 * Editorial-inspired Markdown renderer with soft brutalist accents.
 * Design direction: Magazine layout meets Swiss typography with sage green accents.
 *
 * Aesthetic: Refined minimalism with intentional asymmetry and generous whitespace.
 */

import { useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

interface DailyMarkdownProps {
  date: string // "YYYY-MM-DD"
  showJSON?: boolean
}

interface MarkdownSection {
  type: 'heading' | 'paragraph' | 'emoji-heading' | 'list' | 'divider'
  content: string
  emoji?: string
  level?: number
  items?: string[]
}

export default function DailyMarkdown({ date, showJSON = false }: DailyMarkdownProps) {
  const [markdown, setMarkdown] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [viewMode, setViewMode] = useState<'markdown' | 'json'>(showJSON ? 'json' : 'markdown')

  useEffect(() => {
    const loadMarkdown = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('인증이 필요합니다')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${API_URL}/api/daily/${date}/markdown`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })

        if (!response.ok) {
          throw new Error('콘텐츠를 불러오는 데 실패했습니다')
        }

        const data = await response.json()
        setMarkdown(data.markdown || '')
        setIsLoading(false)
      } catch (err: any) {
        setError(err.message || '오류가 발생했습니다')
        setIsLoading(false)
      }
    }

    loadMarkdown()
  }, [date])

  const parseMarkdown = (md: string): MarkdownSection[] => {
    const lines = md.split('\n')
    const sections: MarkdownSection[] = []
    let currentList: string[] = []

    const flushList = () => {
      if (currentList.length > 0) {
        sections.push({ type: 'list', content: '', items: currentList })
        currentList = []
      }
    }

    lines.forEach((line) => {
      const trimmed = line.trim()

      // Empty line
      if (!trimmed) {
        flushList()
        return
      }

      // Divider
      if (trimmed === '---') {
        flushList()
        sections.push({ type: 'divider', content: '' })
        return
      }

      // Emoji heading (🏃 건강/운동)
      const emojiHeadingMatch = trimmed.match(/^([\u{1F300}-\u{1F9FF}])\s+(.+)$/u)
      if (emojiHeadingMatch) {
        flushList()
        sections.push({
          type: 'emoji-heading',
          content: emojiHeadingMatch[2],
          emoji: emojiHeadingMatch[1]
        })
        return
      }

      // Heading (## 제목)
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/)
      if (headingMatch) {
        flushList()
        sections.push({
          type: 'heading',
          content: headingMatch[2],
          level: headingMatch[1].length
        })
        return
      }

      // List item (- 항목 or * 항목)
      const listMatch = trimmed.match(/^[-*]\s+(.+)$/)
      if (listMatch) {
        currentList.push(listMatch[1])
        return
      }

      // Paragraph
      flushList()
      sections.push({ type: 'paragraph', content: trimmed })
    })

    flushList()
    return sections
  }

  const renderSection = (section: MarkdownSection, index: number) => {
    switch (section.type) {
      case 'heading':
        const HeadingTag = `h${section.level}` as keyof JSX.IntrinsicElements
        const headingClasses = {
          1: 'text-4xl md:text-5xl font-light tracking-tight text-stone-900 mb-8 mt-12',
          2: 'text-2xl md:text-3xl font-normal tracking-tight text-stone-800 mb-6 mt-10',
          3: 'text-xl md:text-2xl font-medium text-stone-700 mb-4 mt-8',
          4: 'text-lg md:text-xl font-medium text-stone-600 mb-3 mt-6',
          5: 'text-base md:text-lg font-semibold text-stone-500 mb-2 mt-4',
          6: 'text-sm md:text-base font-semibold uppercase tracking-wide text-stone-400 mb-2 mt-4'
        }[section.level || 2]

        return (
          <HeadingTag key={index} className={headingClasses}>
            {section.content}
          </HeadingTag>
        )

      case 'emoji-heading':
        return (
          <div key={index} className="flex items-start gap-4 mb-6 mt-10 group">
            <div className="text-4xl transition-transform group-hover:scale-110 group-hover:rotate-12 duration-300">
              {section.emoji}
            </div>
            <div className="flex-1">
              <h3 className="text-xl md:text-2xl font-medium text-stone-800 pt-1 mb-1">
                {section.content}
              </h3>
              <div className="h-0.5 bg-gradient-to-r from-sage-400 to-transparent w-16 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
          </div>
        )

      case 'paragraph':
        // Check for bold patterns (**text**)
        const parts = section.content.split(/(\*\*[^*]+\*\*)/)
        return (
          <p key={index} className="text-base md:text-lg leading-relaxed text-stone-700 mb-4">
            {parts.map((part, i) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return (
                  <strong key={i} className="font-semibold text-stone-900">
                    {part.slice(2, -2)}
                  </strong>
                )
              }
              return part
            })}
          </p>
        )

      case 'list':
        return (
          <ul key={index} className="space-y-3 mb-6 ml-1">
            {section.items?.map((item, i) => (
              <li key={i} className="flex items-start gap-4 group">
                <span className="text-sage-500 mt-1.5 flex-shrink-0 text-xs transition-colors group-hover:text-sage-600">
                  ◆
                </span>
                <span className="text-base md:text-lg text-stone-700 leading-relaxed transition-colors group-hover:text-stone-900">
                  {item}
                </span>
              </li>
            ))}
          </ul>
        )

      case 'divider':
        return (
          <div key={index} className="my-12 flex items-center gap-4">
            <div className="h-px bg-gradient-to-r from-transparent via-stone-300 to-transparent flex-1" />
            <div className="w-1.5 h-1.5 rounded-full bg-sage-400" />
            <div className="h-px bg-gradient-to-r from-transparent via-stone-300 to-transparent flex-1" />
          </div>
        )

      default:
        return null
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream-50">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-2 border-sage-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-stone-600 font-light tracking-wide">오늘의 리듬을 불러오는 중</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-cream-50">
        <Card className="p-8 max-w-md mx-auto border-red-200 bg-red-50">
          <p className="text-red-700 font-medium">{error}</p>
        </Card>
      </div>
    )
  }

  const sections = parseMarkdown(markdown)

  return (
    <div className="min-h-screen bg-cream-50 relative">
      {/* Subtle background texture */}
      <div className="fixed inset-0 opacity-30 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-sage-50 via-transparent to-stone-100" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-sage-200 rounded-full blur-3xl opacity-20" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-stone-300 rounded-full blur-3xl opacity-10" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-stone-200 shadow-sm relative">
        <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-light tracking-tight text-stone-900">오늘의 리듬</h1>
            <p className="text-sm text-stone-500 mt-0.5 font-light">{date}</p>
          </div>

          {/* View Toggle */}
          <div className="flex gap-2">
            <Button
              onClick={() => setViewMode('markdown')}
              variant={viewMode === 'markdown' ? 'default' : 'outline'}
              className={viewMode === 'markdown'
                ? 'bg-sage-600 hover:bg-sage-700 text-white border-0'
                : 'border-stone-300 text-stone-600 hover:bg-stone-100'
              }
            >
              Markdown
            </Button>
            <Button
              onClick={() => setViewMode('json')}
              variant={viewMode === 'json' ? 'default' : 'outline'}
              className={viewMode === 'json'
                ? 'bg-sage-600 hover:bg-sage-700 text-white border-0'
                : 'border-stone-300 text-stone-600 hover:bg-stone-100'
              }
            >
              JSON
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-12 md:py-20 relative">
        {viewMode === 'markdown' ? (
          <article className="prose-custom">
            {/* Date Badge */}
            <div className="inline-block px-4 py-2 bg-sage-100 text-sage-800 text-sm font-medium tracking-wide mb-12 rounded-sm">
              {new Date(date).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
              })}
            </div>

            {/* Rendered Sections */}
            <div className="space-y-1">
              {sections.map((section, index) => renderSection(section, index))}
            </div>

            {/* Bottom Spacer */}
            <div className="h-20" />
          </article>
        ) : (
          <Card className="p-8 bg-stone-900 border-0 shadow-2xl">
            <pre className="text-xs md:text-sm text-emerald-400 font-mono overflow-x-auto whitespace-pre-wrap">
              {markdown}
            </pre>
          </Card>
        )}
      </main>

      {/* Custom Styles */}
      <style jsx global>{`
        @layer utilities {
          .bg-cream-50 {
            background-color: #fafaf8;
          }
          .bg-sage-50 {
            background-color: #f4f7f5;
          }
          .bg-sage-100 {
            background-color: #e8f0ea;
          }
          .bg-sage-200 {
            background-color: #d1e3d5;
          }
          .text-sage-500 {
            color: #6b8e75;
          }
          .text-sage-600 {
            color: #5a7a62;
          }
          .bg-sage-600 {
            background-color: #5a7a62;
          }
          .hover\\:bg-sage-700:hover {
            background-color: #4a6552;
          }
          .text-sage-800 {
            color: #3a5142;
          }
          .border-sage-500 {
            border-color: #6b8e75;
          }
          .bg-sage-400 {
            background-color: #7ea288;
          }
          .from-sage-400 {
            --tw-gradient-from: #7ea288;
            --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(126, 162, 136, 0));
          }
          .from-sage-50 {
            --tw-gradient-from: #f4f7f5;
            --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to, rgba(244, 247, 245, 0));
          }
        }

        @font-face {
          font-family: 'Instrument Serif';
          src: local('Georgia'), local('Times New Roman');
          font-display: swap;
        }

        .prose-custom {
          font-family: 'Instrument Serif', Georgia, serif;
          line-height: 1.75;
        }

        /* Smooth scroll */
        html {
          scroll-behavior: smooth;
        }

        /* Selection color */
        ::selection {
          background-color: #e8f0ea;
          color: #3a5142;
        }

        /* Print styles */
        @media print {
          .sticky {
            position: relative;
          }
          .bg-cream-50 {
            background-color: white;
          }
          .shadow-sm,
          .shadow-2xl {
            box-shadow: none;
          }
        }
      `}</style>
    </div>
  )
}
