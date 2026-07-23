import os
import json
import yaml
import ollama
from pydantic import BaseModel
from typing import List

# Cấu hình đường dẫn thư mục tài liệu
DOCS_DIR = "raw"
OUTPUT_FILE = "generated_dataset.yaml"
MODEL_NAME = "llama3.2"  # có thể đổi sang model mạnh hơn, xem ghi chú cuối file


class QAItem(BaseModel):
    question: str
    rubric: str


class QAList(BaseModel):
    items: List[QAItem]

GENERATOR_SYSTEM_PROMPT = """
Bạn là một kỹ sư QA chuyên tạo test case cho ứng dụng RAG/AI.
Dựa vào tài liệu được cung cấp, hãy tạo ra 3 cặp (Câu hỏi - Tiêu chí kiểm thử):
1. Một câu hỏi trực tiếp có trong bài.
2. Một câu hỏi tóm tắt/tổng hợp.
3. Một câu hỏi bẫy về nội dung KHÔNG CÓ trong bài.

Yêu cầu trả về định dạng JSON theo đúng schema:
{
  "items": [
    {
      "question": "Nội dung câu hỏi",
      "rubric": "Tiêu chí để câu trả lời đạt PASS (Ví dụ: Trả lời chính xác..., Từ chối nếu thiếu thông tin...)"
    }
  ]
}
"""

def generate_test_cases_for_file(file_path, file_name):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc_snippet = content[:3000]
    prompt = f"Tài liệu:\n{doc_snippet}"
    
    response = ollama.chat(
        model=MODEL_NAME,
        format=QAList.model_json_schema(),  # ép cứng cấu trúc ở tầng decode, không còn "đoán" cấu trúc
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.2}
    )

    test_cases = []
    raw_text = response['message']['content']

    try:
        parsed = QAList.model_validate_json(raw_text)

        if not parsed.items:
            print(f"  [Cảnh báo] Model trả về danh sách rỗng cho file {file_name}")

        for item in parsed.items:
            test_cases.append({
                "vars": {
                    "context": f"file://./raw/{file_name}",
                    "question": item.question
                },
                "assert": [
                    {
                        "type": "llm-rubric",
                        "value": item.rubric,
                        "provider": f"ollama:chat:{MODEL_NAME}"
                    }
                ]
            })

    except Exception as e:
        # Với format=schema lỗi này gần như không còn xảy ra, nhưng vẫn giữ
        # lại để bắt trường hợp model bị timeout / trả về rỗng hoàn toàn.
        print(f"  Lỗi validate output file {file_name}: {e}")
        print(f"  --- Raw text model trả về (để debug) ---\n{raw_text}\n--- Hết raw text ---")

    return test_cases

def main():
    all_tests = []
    
    for file_name in os.listdir(DOCS_DIR):
        if file_name.endswith(".md") or file_name.endswith(".txt"):
            print(f"Đang tạo test cases cho: {file_name}...")
            file_path = os.path.join(DOCS_DIR, file_name)
            cases = generate_test_cases_for_file(file_path, file_name)
            all_tests.extend(cases)

    # Ghi ra file YAML dùng cho Promptfoo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(all_tests, f, allow_unicode=True, sort_keys=False)

    print(f"\n Hoàn tất! Đã tạo {len(all_tests)} test cases lưu vào tệp '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()