'use client';

import { useState, useEffect } from 'react';
import type { DailyContent } from '@/lib/content/types';

export default function ComparisonPage() {
  const [jsonContent, setJsonContent] = useState<DailyContent | null>(null);
  const [markdownContent, setMarkdownContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadContent() {
      try {
        // JSON 파일 로드
        const jsonRes = await fetch('/data/2026-01-31_simple.json');
        const jsonData = await jsonRes.json();
        setJsonContent(jsonData);

        // Markdown 파일 로드
        const mdRes = await fetch('/data/2026-01-31_new_format.md');
        const mdText = await mdRes.text();
        setMarkdownContent(mdText);

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : '파일 로드 실패');
        setLoading(false);
      }
    }

    loadContent();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500">에러: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">
          일간 콘텐츠 포맷 비교
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 왼쪽: 기존 JSON 포맷 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">기존 JSON 포맷</h2>
              <span className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded">
                6.2KB, 166줄
              </span>
            </div>
            <div className="prose prose-sm max-w-none overflow-y-auto max-h-[800px]">
              {jsonContent && (
                <div className="space-y-6">
                  {/* 요약 */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">요약</h3>
                    <p className="text-gray-700">{jsonContent.summary}</p>
                  </div>

                  {/* 키워드 */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">키워드</h3>
                    <div className="flex flex-wrap gap-2">
                      {jsonContent.keywords.map((keyword, idx) => (
                        <span
                          key={idx}
                          className="bg-gray-100 px-3 py-1 rounded-full text-sm"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 리듬 해설 */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">리듬 해설</h3>
                    <p className="text-gray-700">{jsonContent.rhythm_description}</p>
                  </div>

                  {/* 집중/주의 포인트 */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">집중/주의 포인트</h3>
                    <div className="space-y-2">
                      <div>
                        <h4 className="font-medium text-green-700">집중</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700">
                          {jsonContent.focus_caution.focus.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-red-700">주의</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700">
                          {jsonContent.focus_caution.caution.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* 행동 가이드 */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">행동 가이드</h3>
                    <div className="space-y-2">
                      <div>
                        <h4 className="font-medium text-green-700">권장</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700">
                          {jsonContent.action_guide.do.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-red-700">지양</h4>
                        <ul className="list-disc list-inside text-sm text-gray-700">
                          {jsonContent.action_guide.avoid.map((item, idx) => (
                            <li key={idx}>{item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* 건강/운동 */}
                  <div className="bg-green-50 p-4 rounded">
                    <h3 className="text-lg font-semibold mb-2">🏃 건강/운동</h3>
                    <div className="text-sm space-y-1">
                      <p><strong>권장:</strong> {jsonContent.daily_health_sports.recommended_activities.join(', ')}</p>
                      <p className="text-gray-600">{jsonContent.daily_health_sports.explanation}</p>
                    </div>
                  </div>

                  {/* 음식/영양 */}
                  <div className="bg-orange-50 p-4 rounded">
                    <h3 className="text-lg font-semibold mb-2">🍜 음식/영양</h3>
                    <div className="text-sm space-y-1">
                      <p><strong>권장:</strong> {jsonContent.daily_meal_nutrition.recommended_foods.join(', ')}</p>
                      <p><strong>지양:</strong> {jsonContent.daily_meal_nutrition.avoid_foods.join(', ')}</p>
                      <p className="text-gray-600">{jsonContent.daily_meal_nutrition.explanation}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 오른쪽: 새 Markdown 포맷 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">새 Markdown 포맷</h2>
              <span className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded">
                4.8KB, 123줄
              </span>
            </div>
            <div className="prose prose-sm max-w-none overflow-y-auto max-h-[800px]">
              <div className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                {markdownContent.split('\n').map((line, idx) => {
                  // 제목 처리
                  if (line.startsWith('# ')) {
                    return (
                      <h1 key={idx} className="text-2xl font-bold mt-6 mb-4">
                        {line.substring(2)}
                      </h1>
                    );
                  }
                  if (line.startsWith('## ')) {
                    return (
                      <h2 key={idx} className="text-xl font-semibold mt-4 mb-2">
                        {line.substring(3)}
                      </h2>
                    );
                  }
                  if (line.startsWith('### ')) {
                    return (
                      <h3 key={idx} className="text-lg font-medium mt-3 mb-2">
                        {line.substring(4)}
                      </h3>
                    );
                  }
                  // 리스트 처리
                  if (line.startsWith('- ')) {
                    return (
                      <li key={idx} className="ml-4 text-gray-700">
                        {line.substring(2)}
                      </li>
                    );
                  }
                  // 굵은 글씨 처리
                  if (line.includes('**')) {
                    const parts = line.split('**');
                    return (
                      <p key={idx} className="mb-2">
                        {parts.map((part, i) =>
                          i % 2 === 1 ? (
                            <strong key={i}>{part}</strong>
                          ) : (
                            <span key={i}>{part}</span>
                          )
                        )}
                      </p>
                    );
                  }
                  // 구분선
                  if (line === '---') {
                    return <hr key={idx} className="my-4 border-gray-300" />;
                  }
                  // 빈 줄
                  if (line.trim() === '') {
                    return <br key={idx} />;
                  }
                  // 일반 텍스트
                  return (
                    <p key={idx} className="mb-2 text-gray-700">
                      {line}
                    </p>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* 비교 통계 */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4">📊 비교 통계</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <h3 className="font-semibold mb-2">기존 JSON</h3>
              <ul className="text-sm space-y-1">
                <li>• 크기: 6.2KB</li>
                <li>• 줄 수: 166줄</li>
                <li>• 글자 수: ~570자</li>
                <li>• 점수: 68%</li>
              </ul>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <h3 className="font-semibold mb-2">새 Markdown ⭐</h3>
              <ul className="text-sm space-y-1">
                <li>• 크기: 4.8KB</li>
                <li>• 줄 수: 123줄</li>
                <li>• 글자 수: ~860자 ✅</li>
                <li>• 점수: 89%</li>
              </ul>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <h3 className="font-semibold mb-2">주요 차이점</h3>
              <ul className="text-sm space-y-1">
                <li>✅ Markdown이 더 읽기 쉬움</li>
                <li>✅ 글자 수 요구사항 충족</li>
                <li>✅ PDF 변환 용이</li>
                <li>✅ 이모지로 시각적 구분</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
