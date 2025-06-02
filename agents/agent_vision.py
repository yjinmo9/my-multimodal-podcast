from openai import OpenAI
import base64
import os
from typing import Optional
from langfuse import Langfuse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def describe_image(image_path: str, langfuse_trace: Optional[any] = None) -> str:
    span = langfuse_trace.span(name=f"Describe Image: {os.path.basename(image_path)}") if langfuse_trace else None

    try:
        # 이미지 base64 인코딩
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded_image = base64.b64encode(image_data).decode("utf-8")

        # GPT-4o Vision 입력
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 이미지를 구체적으로 분석해줘. "
                                    "사진 속에 누가 있는지, 인물들의 표정과 자세는 어떤지, "
                                    "각 인물이 들고 있는 물건이나 주변에 놓인 사물은 무엇인지, "
                                    "배경이나 장소의 분위기와 상황은 어떤지 차근차근 설명해줘. "
                                    "전체적인 상황을 파악할 수 있게 스토리처럼 연결해서 말해줘."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{encoded_image}"}
                        }
                    ]
                }
            ],
            max_tokens=300
        )

        result = response.choices[0].message.content

        if span:
            span.output = {"description": result}
            span.end()

        return result

    except Exception as e:
        print(f"❌ 이미지 분석 실패 ({image_path}):", e)
        if span:
            span.output = {"error": str(e)}
            span.end()
        return "분석 실패"
