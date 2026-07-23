# CHƯƠNG 2: NỀN TẢNG KỸ THUẬT


## 2.1 Nền tảng Python cần thiết

Trước khi học AI Agent, cần vững các kỹ năng Python sau:

  2.1.1 Python cơ bản (bắt buộc)
    - OOP: class, kế thừa, decorator, dataclass
    - Async/await: asyncio, aiohttp (agent thường chạy bất đồng bộ)
    - Type hints: typing module (code agent cần rõ ràng về kiểu dữ liệu)
    - Environment management: venv, dotenv, quản lý secrets

  2.1.2 Thư viện cần thiết
    - requests / httpx   : gọi API REST
    - pydantic           : validate và parse dữ liệu có cấu trúc
    - json / yaml        : xử lý config và output của LLM
    - logging            : ghi log hành động của agent

  Ví dụ: Gọi Anthropic API thủ công (không dùng framework)
  ----------------------------------------------------------
  import anthropic

  client = anthropic.Anthropic(api_key="sk-ant-...")

  message = client.messages.create(
      model="claude-sonnet-4-6",
      max_tokens=1024,
      messages=[{"role": "user", "content": "Tóm tắt bài báo sau: ..."}]
  )
  print(message.content[0].text)

## 2.2 Hiểu LLM ở mức kỹ thuật

  2.2.1 Tokenization
    - LLM không đọc từ, mà đọc token (mảnh từ)
    - 1 token ≈ 0.75 từ tiếng Anh, tiếng Việt thường nhiều token hơn
    - Context window: giới hạn số token LLM xử lý được mỗi lần
    - Ảnh hưởng đến: chi phí, tốc độ, khả năng nhớ của agent

  2.2.2 Temperature & Sampling
    - temperature=0   : tất định, tái lặp được (dùng cho agent logic)
    - temperature=0.7 : cân bằng sáng tạo/ổn định
    - temperature=1.0+: sáng tạo cao, không ổn định
    → Với agent cần ra quyết định chính xác: dùng temperature thấp (0–0.2)

  2.2.3 System Prompt vs User Prompt
    - System: định nghĩa vai trò, hành vi, quy tắc của agent
    - User  : đầu vào từ người dùng hoặc từ agent khác
    - Assistant: lịch sử phản hồi (dùng cho multi-turn)

  2.2.4 Structured Output
    Agent cần output có cấu trúc để xử lý tiếp:

    Cách 1 – JSON mode:
      Yêu cầu LLM trả về JSON hợp lệ
      → parse bằng json.loads()

    Cách 2 – Function calling / Tool use:
      Định nghĩa schema trước, LLM điền tham số
      → đảm bảo output đúng format

    Cách 3 – Pydantic parsing:
      Dùng instructor library để ép LLM trả về Pydantic model

## 2.3 Prompt Engineering cho Agent

  2.3.1 Chain-of-Thought (CoT)
    Yêu cầu LLM "suy nghĩ từng bước" trước khi trả lời:

    Ví dụ:
      "Hãy giải quyết bài toán sau từng bước một.
       Bước 1: Xác định thông tin đã cho
       Bước 2: Xác định thông tin cần tìm
       Bước 3: Lập kế hoạch giải
       Bước 4: Thực hiện
       Bước 5: Kiểm tra kết quả"

  2.3.2 ReAct Pattern (Reason + Act)
    Agent luân phiên giữa suy luận và hành động:

    Thought: Tôi cần tìm giá cổ phiếu VNM hôm nay
    Action : search_web("VNM stock price today")
    Observation: Giá VNM = 72,500 VND
    Thought: Đã có dữ liệu, tôi cần so sánh với hôm qua
    Action : search_web("VNM stock price yesterday")
    Observation: Giá hôm qua = 71,000 VND
    Thought: Tăng 2.1%, tôi có thể trả lời
    Answer : Cổ phiếu VNM tăng 2.1% so với hôm qua...

  2.3.3 Few-shot Prompting
    Cung cấp ví dụ mẫu cho agent:
      Input : "Phân loại email: 'Hóa đơn tháng 5 đã sẵn sàng'"
      Output: {"category": "billing", "priority": "medium"}

      Input : "Phân loại email: 'Server sập khẩn cấp!'"
      Output: {"category": "incident", "priority": "critical"}

      Input : [email mới của người dùng]
      Output: ???

  2.3.4 System Prompt template cho Agent
    ----------------------------------------
    Bạn là [TÊN_AGENT], một [VAI_TRÒ].

    NHIỆM VỤ:
    [Mô tả rõ ràng nhiệm vụ]

    CÔNG CỤ BẠN CÓ:
    - [tool_1]: [mô tả]
    - [tool_2]: [mô tả]

    QUY TẮC:
    1. Luôn kiểm tra dữ liệu trước khi hành động
    2. Nếu không chắc, hỏi người dùng
    3. Không thực hiện hành động không thể hoàn tác nếu chưa xác nhận

    ĐỊNH DẠNG OUTPUT:
    [Chỉ rõ format JSON, markdown, hoặc plain text]
    ----------------------------------------

## 2.4 Tool Calling (Function Calling)

  Đây là kỹ năng cốt lõi của AI Agent – cho phép LLM "sử dụng công cụ".

  2.4.1 Cơ chế hoạt động
    1. Developer định nghĩa tool với tên, mô tả, và schema tham số
    2. LLM đọc danh sách tool và mô tả
    3. Khi cần, LLM sinh ra lời gọi tool (tên + tham số)
    4. Developer thực thi tool thực sự
    5. Kết quả trả lại cho LLM tiếp tục xử lý

  2.4.2 Ví dụ định nghĩa tool với Anthropic SDK
    tools = [
      {
        "name": "get_weather",
        "description": "Lấy thông tin thời tiết hiện tại tại một thành phố",
        "input_schema": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "Tên thành phố, ví dụ: 'Ho Chi Minh City'"
            }
          },
          "required": ["city"]
        }
      }
    ]

  2.4.3 Vòng lặp tool-calling đầy đủ
    while True:
        response = llm.call(messages=messages, tools=tools)

        if response.stop_reason == "end_turn":
            break  # Agent hoàn thành

        if response.stop_reason == "tool_use":
            for tool_call in response.tool_calls:
                result = execute_tool(tool_call.name, tool_call.input)
                messages.append(tool_result_message(tool_call.id, result))

## 2.5 Memory trong AI Agent

  2.5.1 Bốn loại memory
    (a) In-context memory (ngắn hạn)
        - Là messages[] trong API call
        - Giới hạn bởi context window
        - Mất khi kết thúc session

    (b) External memory (dài hạn)
        - Lưu vào database, file, vector store
        - Truy xuất khi cần qua RAG
        - Không giới hạn kích thước

    (c) Episodic memory
        - Ghi nhớ các sự kiện đã xảy ra
        - "Lần trước người dùng hỏi về X, tôi đã làm Y"

    (d) Semantic memory
        - Kiến thức domain được embed vào vector store
        - Truy xuất bằng similarity search

  2.5.2 Vector Database cho long-term memory
    Công cụ phổ biến:
      - Chroma   : đơn giản, chạy local, phù hợp học tập
      - Pinecone : cloud, production-ready
      - Weaviate : open-source, tính năng phong phú
      - Qdrant   : hiệu năng cao, hỗ trợ filter tốt
      - FAISS    : của Meta, chạy local, rất nhanh

    Quy trình RAG cơ bản:
      1. Chunk văn bản thành đoạn nhỏ (~500 tokens)
      2. Embed mỗi chunk thành vector (dùng embedding model)
      3. Lưu vào vector DB
      4. Khi agent cần thông tin: embed query → tìm chunk gần nhất
      5. Đưa chunk vào context → LLM trả lời

## 2.6 Đánh giá Agent (Evaluation)

  Không thể cải thiện cái không đo lường được!

  2.6.1 Các metric cơ bản
    - Task completion rate : tỷ lệ hoàn thành nhiệm vụ
    - Step efficiency      : số bước thực tế / số bước tối ưu
    - Tool usage accuracy  : gọi đúng tool, đúng tham số
    - Hallucination rate   : tỷ lệ sinh thông tin sai
    - Latency              : thời gian hoàn thành
    - Cost per task        : chi phí token trung bình mỗi task

  2.6.2 Framework đánh giá
    - LangSmith  : tracing, monitoring cho LangChain
    - Weights & Biases : MLOps, log experiment
    - Custom eval set : tự xây dựng bộ test case

## 2.7 Tóm tắt chương

  Nền tảng cần có trước khi học framework:
    ✓ Python vững (OOP, async, type hints)
    ✓ Hiểu tokenization, temperature, context window
    ✓ Biết viết prompt hiệu quả (CoT, ReAct, few-shot)
    ✓ Implement tool calling từ scratch
    ✓ Hiểu 4 loại memory và khi nào dùng loại nào
    ✓ Biết đo lường hiệu quả agent

