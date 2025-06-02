import sys
import os
from agent_generate_followup import generate_followup_script
from agent_tts import synthesize_voice

# Langfuse 연동
from langfuse import Langfuse
from uuid import uuid4

def main():
    # 입력 인자 받기
    script_path = sys.argv[1]
    question = sys.argv[2]
    output_mp3_path = sys.argv[3]

    # ✅ Langfuse 초기화 및 트레이스 생성
    langfuse = Langfuse()
    trace = langfuse.trace(
        trace_id=str(uuid4()),
        name="FollowupGeneration",
        input={"question": question}
    )

    # ✅ Step 1: 스크립트 로드
    print("📖 원본 스크립트 불러오는 중...")
    span_load = trace.span(name="Load Script")
    with open(script_path, "r") as f:
        original_script = f.read()
    span_load.end()

    # ✅ Step 2: 후속 스크립트 생성
    print(f"💬 선택된 질문: {question}")
    span_gen = trace.span(name="Generate Followup Script")
    followup_script = generate_followup_script(original_script, question)
    span_gen.output = {"followup_script": followup_script}
    span_gen.end()

    # ✅ Step 3: TTS 변환
    print("🎙️ 음성 변환 중...")
    span_tts = trace.span(name="TTS")
    synthesize_voice(followup_script, output_mp3_path)
    span_tts.output = {"output_path": output_mp3_path}
    span_tts.end()

    print("✅ 후속 팟캐스트 저장 완료:", output_mp3_path)

    # ✅ 트레이스 종료
    trace.output = {
    "status": "success",
        "output_path": output_mp3_path
    }
 

if __name__ == "__main__":
    main()
