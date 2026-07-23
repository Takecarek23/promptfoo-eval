# CHƯƠNG 1: TỔNG QUAN VỀ AI AGENT


## 1.1 AI Agent là gì?

AI Agent (tác nhân trí tuệ nhân tạo) là một hệ thống phần mềm có khả năng
tự động nhận thức môi trường, đưa ra quyết định và thực hiện hành động để
đạt được mục tiêu được giao mà không cần sự can thiệp liên tục của con người.

Định nghĩa chính thức:
  Agent = Perception (nhận thức) + Reasoning (suy luận) + Action (hành động)

Sự khác biệt so với chatbot thông thường:
  - Chatbot: nhận input → sinh output (phản xạ đơn thuần)
  - AI Agent: nhận mục tiêu → lập kế hoạch → thực thi nhiều bước → đánh giá kết quả

## 1.2 Phân loại AI Agent

1.2.1 Theo mức độ tự chủ
  [Mức 1] Rule-based Agent    : hoạt động theo luật cố định (if-then)
  [Mức 2] Reactive Agent      : phản ứng theo trạng thái hiện tại
  [Mức 3] Deliberative Agent  : có mô hình thế giới, lập kế hoạch trước
  [Mức 4] Learning Agent      : học từ kinh nghiệm, cải thiện theo thời gian
  [Mức 5] Autonomous LLM Agent: sử dụng LLM làm "não", tự lập kế hoạch phức tạp

1.2.2 Theo kiến trúc
  - Single Agent   : một agent duy nhất xử lý toàn bộ task
  - Multi-Agent    : nhiều agent phối hợp, mỗi agent chuyên một vai trò
  - Hierarchical   : agent cấp cao điều phối các agent cấp thấp hơn

## 1.3 Vì sao AI Agent đang bùng nổ?

Các yếu tố thúc đẩy (2023–2026):
  (a) LLM mạnh hơn: GPT-4, Claude 3, Gemini Ultra có khả năng lập luận tốt
  (b) Tool use: LLM có thể gọi API, tra cứu web, chạy code
  (c) Long context: xử lý được tài liệu dài, duy trì trạng thái lâu hơn
  (d) Frameworks trưởng thành: LangChain, LlamaIndex, CrewAI, AutoGen
  (e) Nhu cầu thực tế: tự động hóa workflow, RPA thế hệ mới

## 1.4 Ứng dụng thực tế của AI Agent

  Lĩnh vực          | Ứng dụng tiêu biểu
  ------------------|------------------------------------------
  Lập trình         | Devin, GitHub Copilot Workspace
  Nghiên cứu        | Perplexity Deep Research, Elicit
  Kinh doanh        | Agent tự động hóa email, CRM, báo cáo
  Y tế              | Hỗ trợ chẩn đoán, tổng hợp y văn
  Giáo dục          | Gia sư cá nhân hóa, chấm bài tự động
  Tài chính         | Agent phân tích thị trường, trading

## 1.5 Kiến trúc tổng quát của một LLM-based Agent


  ┌─────────────────────────────────────────────┐
  │                  LLM Core                   │
  │         (Brain – Reasoning Engine)          │
  └──────────┬──────────────────────┬───────────┘
             │                      │
    ┌────────▼────────┐    ┌────────▼────────┐
    │    Memory       │    │     Tools       │
    │ - Short-term    │    │ - Web search    │
    │ - Long-term     │    │ - Code executor │
    │ - Episodic      │    │ - File I/O      │
    │ - Semantic      │    │ - API calls     │
    └─────────────────┘    └─────────────────┘
             │                      │
             └──────────┬───────────┘
                        │
              ┌─────────▼─────────┐
              │  Planning Module  │
              │ - Task decompose  │
              │ - ReAct / CoT     │
              │ - Self-reflection │
              └───────────────────┘

## 1.6 Các khái niệm cốt lõi cần nắm

  (1) Prompt Engineering   : thiết kế prompt hiệu quả cho agent
  (2) Tool Calling         : cho phép LLM gọi hàm/API bên ngoài
  (3) Memory Management    : quản lý ngữ cảnh ngắn/dài hạn
  (4) Planning & Reasoning : CoT, ReAct, Tree-of-Thoughts
  (5) Evaluation           : đánh giá chất lượng agent
  (6) Safety & Alignment   : kiểm soát hành vi agent

## 1.7 Tóm tắt chương

  - AI Agent = LLM + Memory + Tools + Planning
  - Khác chatbot ở khả năng tự chủ, đa bước, có trạng thái
  - Đang bùng nổ nhờ LLM mạnh + framework hỗ trợ tốt
  - Lộ trình học: nền tảng → framework → nâng cao → dự án thực

