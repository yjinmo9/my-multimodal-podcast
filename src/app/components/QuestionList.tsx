'use client'

import { useEffect, useState } from 'react'
import { Volume2 } from 'lucide-react'

export default function QuestionList() {
  const [questions, setQuestions] = useState<string[]>([])
  const [loadingQuestion, setLoadingQuestion] = useState<string | null>(null)
  const [followupLinks, setFollowupLinks] = useState<{ question: string, url: string }[]>([])

  useEffect(() => {
    fetch('/api/questions')
      .then(res => res.json())
      .then(setQuestions)
  }, [])

  const handleClick = async (question: string) => {
    setLoadingQuestion(question)
    const res = await fetch('/api/followup', {
      method: 'POST',
      body: JSON.stringify({ question }),
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await res.json()
    setLoadingQuestion(null)

    if (data.mp3) {
      setFollowupLinks(prev => [...prev, { question, url: data.mp3 }])
    }
  }

  return (
    <div className="mt-10 space-y-6">
      <div>
        <h2 className="text-xl font-bold flex items-center gap-2">
          💬 후속 질문으로 더 들어보기
        </h2>
        <ul className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {questions.map((q) => (
            <li key={q}>
              <button
                onClick={() => handleClick(q)}
                disabled={loadingQuestion === q}
                className="w-full text-left bg-white border hover:border-blue-500 rounded-lg px-4 py-3 shadow-sm transition flex items-center gap-2 disabled:opacity-60"
              >
                <Volume2 className="w-5 h-5 text-blue-500" />
                {loadingQuestion === q ? '⏳ 생성 중...' : q}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {followupLinks.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">🎙️ 생성된 후속 팟캐스트</h3>
          <div className="space-y-4">
            {followupLinks.map((item, i) => (
              <div key={i} className="bg-gray-50 border rounded-lg px-4 py-3 shadow-sm">
                <p className="text-sm text-gray-600 mb-1">{item.question}</p>
                <audio controls src={item.url} className="w-full" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

