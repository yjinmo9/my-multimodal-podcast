from openai import OpenAI
import os
from typing import Optional
from langfuse import Langfuse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def synthesize_voice(script: str, output_path: str, langfuse_trace: Optional[any] = None):
    span = langfuse_trace.span(name="TTS Generation") if langfuse_trace else None

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=script
        )
        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ 음성 파일 저장 완료: {output_path}")

        if span:
            span.output = {"output_path": output_path}
            span.end()

    except Exception as e:
        print("❌ TTS 변환 실패:", e)
        if span:
            span.output = {"error": str(e)}
            span.end()
