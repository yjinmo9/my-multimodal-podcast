// ✅ src/app/api/questions/route.ts
import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import path from 'path'

export async function GET() {
  const filePath = path.join(process.cwd(), 'public/audio/questions.json')

  try {
    const file = await readFile(filePath, 'utf-8')
    const questions = JSON.parse(file)
    return NextResponse.json(questions)
  } catch (e) {
    console.error('❌ 질문 파일 읽기 실패:', e)
    return NextResponse.json([], { status: 500 })
  }
}

