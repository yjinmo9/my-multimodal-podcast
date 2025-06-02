from openai import OpenAI
import os
from typing import Optional
from langfuse import Langfuse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 👉 trace는 외부에서 주입
def generate_followup_script(
    question: str,
    original_script: str = "",
    langfuse_trace: Optional[any] = None
) -> str:
    span = langfuse_trace.span(name="Generate Followup Script") if langfuse_trace else None

    prompt = f"""
'{question}'이라는 질문에 대해 약 30초 분량의 팟캐스트용 대본을 작성해 주세요.

다음 조건을 반드시 반영해 주세요:

1. 말투 및 분위기  
- 사람과 이야기하듯 친근하고 편안한 톤으로 작성해 주세요.  
- 설명조보다는, 생각을 공유하고 대화를 건네는 느낌을 주세요.  
- 마치 친구와 산책하며 이야기 나누는 듯한 자연스러운 흐름을 지향해 주세요.

2. 관점과 깊이  
- 질문에 대해 단순한 사실 나열이 아닌, 사회적, 개인적, 혹은 철학적인 시각을 녹여 주세요.  
- 청취자가 스스로 고민해볼 수 있도록 명확한 결론 없이 여운을 남기는 마무리를 지향해 주세요.

3. 분량 및 리듬  
- 대본은 약 30초 분량으로 작성해 주세요. (약 300~400자, 문장 5~7개 정도)  
- 문장은 너무 길지 않게, 듣기에 좋은 템포로 작성해 주세요.

4. 참고 스타일  
- 아래의 원본 스크립트와 말투, 화법, 분위기를 참고해 주세요.

원본 스크립트:
{original_script}
    """

    if span:
        span.input = {
            "question": question,
            "original_script": original_script
        }

    try:
        print("📤 GPT 프롬프트 전달 중...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        print("🧠 GPT 응답:\n", content)

        if not content:
            raise ValueError("GPT 응답이 비어 있음")

        if span:
            span.output = {"followup_script": content}
            span.end()

        return content

    except Exception as e:
        print("❌ GPT 생성 실패:", e)
        if span:
            span.output = {"error": str(e)}
            span.end()
        return "후속 질문에 대한 대본 생성에 실패했습니다."
