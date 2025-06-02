from langfuse import Langfuse
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
langfuse = Langfuse()

def generate_unified_script(slide_infos: list[dict]) -> str:
    trace = langfuse.trace(name="generate_unified_script", metadata={"slide_count": len(slide_infos)})
    span = trace.span(name="prompt_gpt4")

    sections = []
    for slide in slide_infos:
        section = f"""[슬라이드 {slide['slide']}]
텍스트:
{slide.get('text_pdf', '')}

OCR 텍스트:
{slide.get('text_ocr', '')}

이미지 설명:
{slide.get('image_description', '')}"""
        sections.append(section)

    full_context = "\n\n".join(sections)

    prompt = f"""다음은 PDF 슬라이드별 텍스트와 이미지에 대한 설명입니다. 이 정보를 모두 활용하여 하나의 유기적인 **팟캐스트 스크립트**를 작성해 주세요. 

스크립트는 아래 조건을 충실히 반영해 주세요:

📌 [1] **전체 형식 및 톤**
- 사람에게 직접 이야기하듯 부드럽고 편안한 말투로 작성해 주세요.
- 너무 과하게 가볍거나, 반대로 딱딱하고 건조한 어투는 지양해 주세요.
- 발표 대본이 아닌, 청취자의 흥미를 끌 수 있는 **스토리텔링형 정보 전달**을 지향해 주세요.

📌 [2] **내용 구성 및 흐름**
- 각 슬라이드의 주요 내용을 **자연스럽게 연결**해 주세요. 슬라이드별로 끊긴 느낌이 들지 않도록 구성해 주세요.
- 슬라이드 번호나 "첫 번째 슬라이드에서는~" 같은 말은 생략해 주세요.
- 논리적 흐름이 끊기지 않도록 전체를 **하나의 흐름 있는 이야기**로 재구성해 주세요.

📌 [3] **분량 및 밀도**
- 전체 스크립트는 **약 1분 분량**으로 작성해 주세요. (예: 약 1분이면 약 140~150자 정도)
- 너무 장황하거나 반복적인 설명은 피하고, **핵심 내용 중심**으로 간결하게 구성해 주세요.
- 각 문장은 짧고 명료하게, 의미 단위별로 나누어 주세요.

📌 [4] **이미지 설명 활용**
- 이미지 설명은 시각적으로 상상할 수 있도록 **간단하고 자연스럽게** 묘사해 주세요.
- 예: “여기서 한눈에 들어오는 그래프가 눈에 띄죠.” / “사람들이 붐비는 거리의 사진이 인상적입니다.”처럼 시청각 보조 자료가 있음을 암시하되 과하게 설명하진 말아 주세요.

📌 [5] **전문 용어 및 개념 설명**
- 전문 용어나 생소한 개념은 **쉬운 비유나 간단한 예시**로 풀어 주세요.
- 청취자는 관련 배경지식이 없을 수 있다는 점을 고려해 주세요.

---

아래는 슬라이드별 텍스트와 이미지 설명입니다. 이 전체 내용을 바탕으로 위 조건을 만족하는 팟캐스트 스크립트를 작성해 주세요:

{full_context}
    """

    span.input = prompt
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        output = response.choices[0].message.content.strip()
        span.output = {"script": output}
        span.end()
        return output
    except Exception as e:
        span.error = str(e)
        span.end()
        raise
