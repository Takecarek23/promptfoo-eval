import os
import yaml
import ollama
from pydantic import BaseModel, Field
from typing import List

# Cấu hình đường dẫn thư mục tài liệu
DOCS_DIR = "raw"
OUTPUT_FILE = "generated_dataset.yaml"
MODEL_NAME = "llama3.2"  # có thể đổi sang model mạnh hơn, xem ghi chú cuối file

# Trọng số mặc định theo loại câu hỏi (khớp với promptfooconfig.yaml)
WEIGHT_BY_TYPE = {
    "direct": 1.5,
    "summary": 2.0,
    "trap": 1.0,
    "ambiguous": 1.0,
}


class QAItem(BaseModel):
    question: str
    rubric: str
    # Loại câu hỏi: direct | summary | trap | ambiguous
    question_type: str = Field(default="direct")
    # Vài từ khóa/cụm từ đặc trưng có trong tài liệu, dùng để tạo assertion
    # contains-any (kiểm tra nhanh, không phạt nếu model paraphrase khác đi
    # miễn còn 1 từ khóa khớp). Để trống với câu hỏi "trap" hoặc "ambiguous".
    keywords: List[str] = Field(default_factory=list)


class QAList(BaseModel):
    items: List[QAItem]


GENERATOR_SYSTEM_PROMPT = """
Bạn là một kỹ sư QA chuyên tạo test case cho ứng dụng RAG/Second-Brain.
Dựa vào tài liệu được cung cấp, hãy tạo ra 4 cặp (Câu hỏi - Tiêu chí kiểm thử):

1. "direct": Một câu hỏi trực tiếp có đáp án rõ ràng trong bài, kèm 2-4
   keywords là cụm từ/thuật ngữ đặc trưng THỰC SỰ xuất hiện trong tài liệu
   (dùng để kiểm tra nhanh, không cần khớp chính xác từng chữ).
2. "summary": Một câu hỏi tóm tắt/tổng hợp nhiều phần trong tài liệu (không
   cần keywords, chỉ cần rubric mô tả đầy đủ các ý phải có).
3. "trap": Một câu hỏi bẫy về nội dung KHÔNG CÓ trong bài. Rubric phải yêu
   cầu câu trả lời từ chối rõ ràng (không bịa thông tin), không có keywords.
4. "ambiguous": Một câu hỏi mơ hồ, thiếu chủ ngữ/ngữ cảnh rõ ràng liên quan
   đến tài liệu (ví dụ dùng đại từ "cái đó", "phần này" mà không nói rõ).
   Rubric phải yêu cầu AI hỏi lại để làm rõ thay vì đoán, không có keywords.

Yêu cầu trả về đúng schema JSON:
{
  "items": [
    {
      "question": "Nội dung câu hỏi",
      "rubric": "Tiêu chí để câu trả lời đạt PASS",
      "question_type": "direct | summary | trap | ambiguous",
      "keywords": ["từ khóa 1", "từ khóa 2"]
    }
  ]
}
"""


def build_assert_block(item: QAItem) -> list:
    """Chuyển 1 QAItem thành list assertion khớp format của
    generated_dataset.yaml / promptfooconfig.yaml (defaultTest đã set
    provider chấm điểm chung, nên KHÔNG cần field provider ở từng assertion)."""
    asserts = []

    if item.keywords:
        asserts.append({
            "type": "contains-any",
            "weight": 0.4,
            "value": item.keywords,
        })

    asserts.append({
        "type": "llm-rubric",
        "weight": WEIGHT_BY_TYPE.get(item.question_type, 1.5),
        "value": item.rubric,
    })

    return asserts


def generate_test_cases_for_file(file_path, file_name):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc_snippet = content[:3000]
    prompt = f"Tài liệu:\n{doc_snippet}"

    response = ollama.chat(
        model=MODEL_NAME,
        format=QAList.model_json_schema(),  # ép cứng cấu trúc ở tầng decode
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
                "assert": build_assert_block(item)
            })

    except Exception as e:
        # Với format=schema lỗi này gần như không còn xảy ra, nhưng vẫn giữ
        # lại để bắt trường hợp model bị timeout / trả về rỗng hoàn toàn.
        print(f"  Lỗi validate output file {file_name}: {e}")
        print(f"  --- Raw text model trả về (để debug) ---\n{raw_text}\n--- Hết raw text ---")

    return test_cases


def main():
    all_tests = []

    for file_name in sorted(os.listdir(DOCS_DIR)):
        if file_name.endswith(".md") or file_name.endswith(".txt"):
            print(f"Đang tạo test cases cho: {file_name}...")
            file_path = os.path.join(DOCS_DIR, file_name)
            cases = generate_test_cases_for_file(file_path, file_name)
            all_tests.extend(cases)

    # Ghi ra file YAML dùng cho Promptfoo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(all_tests, f, allow_unicode=True, sort_keys=False)

    print(f"\n Hoàn tất! Đã tạo {len(all_tests)} test cases lưu vào tệp '{OUTPUT_FILE}'.")
    print(" Lưu ý: script này SẼ GHI ĐÈ toàn bộ generated_dataset.yaml.")
    print(" Nếu bạn đã chỉnh tay các test case (weight, câu hỏi bẫy đa chương,")
    print(" câu hỏi tổng hợp...), hãy backup file cũ trước khi chạy lại script này.")


if __name__ == "__main__":
    main()
