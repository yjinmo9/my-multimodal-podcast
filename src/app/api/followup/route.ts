// ✅ src/app/api/followup/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import path from 'path'
import { promisify } from 'util'

export const runtime = 'nodejs'
const execAsync = promisify(exec)

export async function POST(req: NextRequest) {
  const body = await req.json()
  const question = body.question

  if (!question) {
    return NextResponse.json({ error: 'Missing question' }, { status: 400 })
  }

  // ✅ sanitize filename
  const safeFilename = question.replace(/[^a-zA-Z0-9가-힣_-]/g, '_').slice(0, 30)
  const scriptPath = path.join(process.cwd(), 'public', 'audio', 'script.txt')
  const outputPath = path.join(process.cwd(), 'public', 'audio', 'followups', `${safeFilename}.mp3`)

  const cmd = `PYTHONPATH=. python3 agents/run_followup.py "${scriptPath}" "${question}" "${outputPath}"`

  try {
    const { stdout } = await execAsync(cmd)
    console.log('✅ Followup created:', stdout)
    return NextResponse.json({ message: 'Followup generated', mp3: `/audio/followups/${safeFilename}.mp3` })
  } catch (e) {
    console.error('❌ Followup error:', e)
    return NextResponse.json({ error: 'Failed to generate followup' }, { status: 500 })
  }
}
