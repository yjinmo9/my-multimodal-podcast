'use client'

import { useState } from 'react'
import QuestionList from './components/QuestionList'

export default function Home() {
  const [audioLinks, setAudioLinks] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [showQuestions, setShowQuestions] = useState(false)
  const [questionKey, setQuestionKey] = useState(0)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setShowQuestions(false) // 이전 질문 숨기기
    const formData = new FormData(e.currentTarget)

    const res = await fetch('/api/generate', {
      method: 'POST',
      body: formData,
    })

    const result = await res.json()
    if (result.links) {
      setAudioLinks(result.links)
      setShowQuestions(true)
      setQuestionKey(prev => prev + 1) // ✅ 질문 새로 불러오도록 key 변경
    }

    setLoading(false)
  }

  return (
    <main className="max-w-xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-6">🎙️ PDF 팟캐스트 생성기</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="block font-medium mb-1">📄 PDF 슬라이드 업로드</span>
          <input type="file" name="pdf" accept="application/pdf" required />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {loading ? '⏳ 생성 중...' : '🎬 팟캐스트 생성하기'}
        </button>
      </form>

      {audioLinks.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">🎧 생성된 통합 팟캐스트:</h2>
          <audio controls src={audioLinks[0]} className="w-full" />
        </div>
      )}

      {/* ✅ 질문은 팟캐스트 생성이 끝난 후에만 표시 */}
      {showQuestions && <QuestionList key={questionKey} />}
    </main>
  )
}
