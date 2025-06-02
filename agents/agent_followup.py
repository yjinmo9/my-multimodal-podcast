from openai import OpenAI
import os
import json
from typing import Optional
from langfuse import Langfuse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# langfuse_trace는 외부에서 주입
def extract_questions_from_script(script: str, langfuse_trace: Optional[any] = None) -> list[str]:
    span = None
    if langfuse_trace:
        span = langfuse_trace.span(name="Generate Follow-up Questions")

    prompt = f"""
다음은 팟캐스트 스크립트입니다.

이 스크립트 내용을 바탕으로, 청취자가 내용을 곱씹으며 스스로 깊이 생각해볼 수 있도록 유도하는 **의미 있는 후속 질문 4개**를 생성해 주세요.  
질문은 단순한 사실 확인이 아니라, **비판적 사고** 또는 **개인적 연결**, **사회적 함의**, **미래에 대한 상상** 등을 자극하는 형태여야 합니다.

예를 들어:
- "당신이라면 이런 상황에서 어떤 선택을 했을까요?"
- "이 개념은 오늘날 우리 사회에 어떻게 적용될 수 있을까요?"
- "비슷한 문제가 지금도 반복되고 있지 않을까요?"
- "이 이야기를 들으며 떠오른 개인적인 경험은 무엇인가요?"  
처럼, 청취자의 내적 성찰이나 토론을 유도하는 **열린 질문(open-ended questions)**으로 구성해 주세요.

❗ 출력은 반드시 **아래 JSON 배열 형식**만 사용해 주세요. 설명이나 부연 없이 배열만 출력해 주세요.:
```json
[
  "질문1",
  "질문2",
  "질문3",
  "질문4"
]
```

스크립트:
{script}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        print("🔥 GPT 응답 내용:\n", content)

        start = content.find("[")
        end = content.rfind("]") + 1
        json_part = content[start:end]
        result = json.loads(json_part)

        if span:  # Langfuse 추적 결과 저장
            span.output = {"questions": result}
            span.end()

        return result

    except Exception as e:
        print("❌ JSON 파싱 실패:", e)

        if span:
            span.output = {"error": str(e)}
            span.end()

        return []