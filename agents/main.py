import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.agent_slide_extract import extract_slide_texts_and_images
from agents.agent_vision import describe_image
from agents.agent_script import generate_unified_script
from agents.agent_tts import synthesize_voice
from agents.agent_followup import extract_questions_from_script

from langfuse import Langfuse

def describe_images_parallel(image_paths: list[str]) -> list[str]:
    results = [None] * len(image_paths)
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_idx = {
            executor.submit(describe_image, path): i
            for i, path in enumerate(image_paths)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                print(f"❌ 이미지 분석 실패 (index {idx}):", e)
                results[idx] = "분석 실패"
    return results

if __name__ == "__main__":
    pdf_path = sys.argv[1]
    slides_dir = "public/slides"
    output_dir = "public/audio"
    os.makedirs(output_dir, exist_ok=True)

    langfuse = Langfuse()
    trace = langfuse.trace(name="PodcastGenerationPipeline", input={"pdf_path": pdf_path})

    # ✅ Slide Extraction
    span1 = trace.span(name="Slide Extraction")
    slide_infos = extract_slide_texts_and_images(pdf_path, slides_dir)
    span1.end()

    # ✅ Image Analysis
    span2 = trace.span(name="Image Analysis (parallel)")
    image_paths = [s["page_image_path"] for s in slide_infos]
    descriptions = describe_images_parallel(image_paths)
    for slide, desc in zip(slide_infos, descriptions):
        slide["image_description"] = desc
    span2.end()

    # ✅ Script Generation
    span3 = trace.span(name="Script Generation")
    script = generate_unified_script(slide_infos)
    script_path = os.path.join(output_dir, "script.txt")
    with open(script_path, "w") as f:
        f.write(script)
    span3.end()

    # ✅ TTS
    span4 = trace.span(name="TTS")
    synthesize_voice(script, os.path.join(output_dir, "episode.mp3"))
    span4.end()

    # ✅ Follow-up Questions
    span5 = trace.span(name="Question Generation")
    questions = extract_questions_from_script(script)
    with open(os.path.join(output_dir, "questions.json"), "w") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    span5.end()

    trace.output = {
    "script_path": script_path,
    "episode": "episode.mp3",
    "questions": questions,
    "pipeline_status": "success"
    }
 
