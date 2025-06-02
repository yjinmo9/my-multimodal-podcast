import { NextRequest, NextResponse } from "next/server";
import { execSync } from "child_process";
import fs from "fs";
import path from "path";

export async function POST(req: NextRequest) {
  console.log("📥 요청 수신됨");

  const formData = await req.formData();
  const file: File | null = formData.get("pdf") as File;

  if (!file) {
    console.error("❌ 업로드된 파일이 없음");
    return NextResponse.json({ error: "파일이 없습니다." }, { status: 400 });
  }

  // 파일 저장
  const arrayBuffer = await file.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  const uploadDir = "public/uploads";
  const uploadPath = path.join(uploadDir, file.name);
  fs.mkdirSync(uploadDir, { recursive: true });
  fs.writeFileSync(uploadPath, buffer);

  console.log(`📄 PDF 저장 완료: ${uploadPath}`);

  try {
    const command = `PYTHONPATH=. python3 agents/main.py "${uploadPath}"`;
    console.log(`🚀 Python 실행 명령: ${command}`);
    execSync(command, { stdio: "inherit" }); // 콘솔에 출력

    // mp3 파일 리스트 수집
    const audioDir = "public/audio";
    const files = fs.readdirSync(audioDir)
      .filter(f => f.endsWith(".mp3"))
      .map(f => `/audio/${f}`);

    console.log("✅ 생성된 mp3:", files);

    return NextResponse.json({ links: files });
  } catch (e: any) {
    console.error("🛑 Python 실행 오류:", e.message);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

