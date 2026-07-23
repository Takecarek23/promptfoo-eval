# CHƯƠNG 3: FRAMEWORKS & TOOLS


## 3.1 Bản đồ hệ sinh thái frameworks

  Tầng 1 – LLM Providers:
    OpenAI, Anthropic, Google, Mistral, Meta (Llama), Ollama (local)

  Tầng 2 – Orchestration Frameworks:
    LangChain, LlamaIndex, Haystack, DSPy

  Tầng 3 – Agent Frameworks:
    LangGraph, CrewAI, AutoGen, Semantic Kernel, Agno

  Tầng 4 – Infrastructure:
    Vector DB (Chroma, Pinecone), Tracing (LangSmith), Deploy (Modal, Fly.io)

## 3.2 LangChain – Framework nền tảng

  Phiên bản hiện tại: LangChain v0.3+ (2025)
  Cài đặt: pip install langchain langchain-anthropic

  3.2.1 Các khái niệm cốt lõi
    (a) Chain
        Chuỗi các bước xử lý nối tiếp nhau:
        prompt_template | llm | output_parser

    (b) Runnable Interface
        Mọi thành phần đều implement .invoke(), .stream(), .batch()
        → dễ kết hợp và thay thế

    (c) LCEL (LangChain Expression Language)
        Dùng ký hiệu | để nối components:

        from langchain_anthropic import ChatAnthropic
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        prompt = ChatPromptTemplate.from_template(
            "Dịch câu sau sang tiếng Anh: {text}"
        )
        model = ChatAnthropic(model="claude-sonnet-4-6")
        parser = StrOutputParser()

        chain = prompt | model | parser
        result = chain.invoke({"text": "Xin chào thế giới"})

    (d) Memory trong LangChain
        - ConversationBufferMemory    : lưu toàn bộ lịch sử
        - ConversationSummaryMemory   : tóm tắt khi quá dài
        - VectorStoreRetrieverMemory  : tìm kiếm ngữ nghĩa

  3.2.2 Agents trong LangChain
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.tools import tool

    @tool
    def search_web(query: str) -> str:
        """Tìm kiếm thông tin trên web."""
        # implement thực tế ở đây
        return f"Kết quả tìm kiếm cho: {query}"

    agent = create_tool_calling_agent(llm, tools=[search_web], prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=[search_web], verbose=True)
    executor.invoke({"input": "Thời tiết Sài Gòn hôm nay thế nào?"})

  3.2.3 Khi nào dùng LangChain?
    ✓ Cần prototype nhanh
    ✓ Tích hợp nhiều loại LLM khác nhau
    ✓ Cần hệ sinh thái integrations phong phú (100+ connector)
    ✗ Không phù hợp cho logic agent phức tạp → dùng LangGraph

## 3.3 LangGraph – Agent có trạng thái phức tạp

  LangGraph là extension của LangChain, dùng để xây dựng agent
  dưới dạng đồ thị có hướng (directed graph).

  Triết lý: Agent = Graph (đỉnh = action, cạnh = điều kiện chuyển trạng thái)

  3.3.1 Khái niệm cốt lõi
    - State    : trạng thái được chia sẻ giữa các node
    - Node     : một bước xử lý (gọi LLM, gọi tool, xử lý kết quả)
    - Edge     : kết nối giữa các node, có thể có điều kiện
    - Graph    : toàn bộ luồng xử lý

  3.3.2 Ví dụ: Agent với vòng lặp ReAct
    from langgraph.graph import StateGraph, END
    from typing import TypedDict, Annotated
    import operator

    class AgentState(TypedDict):
        messages: Annotated[list, operator.add]
        next_action: str

    def call_llm(state: AgentState):
        # Gọi LLM, trả về action tiếp theo
        ...

    def execute_tool(state: AgentState):
        # Thực thi tool được chỉ định
        ...

    def should_continue(state: AgentState):
        if state["next_action"] == "end":
            return END
        return "execute_tool"

    workflow = StateGraph(AgentState)
    workflow.add_node("llm", call_llm)
    workflow.add_node("tool", execute_tool)
    workflow.add_edge("tool", "llm")
    workflow.add_conditional_edges("llm", should_continue)
    workflow.set_entry_point("llm")

    app = workflow.compile()

  3.3.3 Tính năng nổi bật
    - Human-in-the-loop : dừng agent để chờ người dùng xác nhận
    - Checkpointing      : lưu và khôi phục trạng thái agent
    - Streaming          : stream từng bước thực thi
    - Subgraph           : nhúng graph nhỏ vào graph lớn

## 3.4 CrewAI – Multi-Agent Framework

  CrewAI cho phép tạo "đội ngũ" agent phân công vai trò rõ ràng.

  3.4.1 Các thành phần
    - Agent  : có role, goal, backstory, tools riêng
    - Task   : nhiệm vụ cụ thể, giao cho một agent
    - Crew   : tập hợp agents + tasks + quy trình làm việc
    - Process: sequential (tuần tự) hoặc hierarchical (phân cấp)

  3.4.2 Ví dụ: Crew phân tích thị trường
    from crewai import Agent, Task, Crew, Process

    researcher = Agent(
        role="Nhà nghiên cứu thị trường",
        goal="Thu thập dữ liệu thị trường AI Việt Nam năm 2025",
        backstory="Chuyên gia phân tích với 10 năm kinh nghiệm",
        tools=[web_search_tool],
        llm=claude_model
    )

    analyst = Agent(
        role="Nhà phân tích tài chính",
        goal="Phân tích dữ liệu và đưa ra khuyến nghị đầu tư",
        backstory="CFA với kinh nghiệm định giá startup công nghệ",
        llm=claude_model
    )

    task1 = Task(
        description="Nghiên cứu top 10 startup AI tại Việt Nam",
        agent=researcher,
        expected_output="Báo cáo tóm tắt dạng markdown"
    )

    task2 = Task(
        description="Phân tích tiềm năng của từng startup",
        agent=analyst,
        expected_output="Ma trận so sánh và top 3 khuyến nghị"
    )

    crew = Crew(
        agents=[researcher, analyst],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff()

  3.4.3 Khi nào dùng CrewAI?
    ✓ Bài toán có thể chia thành vai trò chuyên biệt
    ✓ Cần nhiều agent làm việc song song hoặc tuần tự
    ✓ Muốn code dễ đọc, dễ bảo trì
    ✗ Không phù hợp khi cần kiểm soát luồng chính xác → dùng LangGraph

## 3.5 AutoGen – Conversational Agent Framework

  AutoGen (Microsoft) cho phép các agent "trò chuyện" với nhau.

  3.5.1 Đặc điểm
    - Agent giao tiếp qua tin nhắn (giống chat)
    - Có thể có người dùng thực tham gia (Human Proxy)
    - Hỗ trợ code execution tích hợp sẵn

  3.5.2 Ví dụ: Pair programming agents
    from autogen import AssistantAgent, UserProxyAgent

    coder = AssistantAgent(
        name="Coder",
        system_message="Bạn là lập trình viên Python chuyên nghiệp.",
        llm_config={"model": "claude-sonnet-4-6"}
    )

    reviewer = AssistantAgent(
        name="Reviewer",
        system_message="Bạn review code và tìm bug.",
        llm_config={"model": "claude-sonnet-4-6"}
    )

    user = UserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        code_execution_config={"work_dir": "coding"}
    )

    user.initiate_chat(
        coder,
        message="Viết hàm tính số Fibonacci dùng dynamic programming"
    )

## 3.6 LlamaIndex – RAG và Knowledge Agent

  Chuyên về xây dựng hệ thống RAG và agent tương tác với dữ liệu.

  3.6.1 Điểm mạnh
    - Data connectors: tải dữ liệu từ 100+ nguồn (PDF, web, DB, API)
    - Advanced RAG   : chunk strategy, reranking, hybrid search
    - Query engines  : trả lời câu hỏi về dữ liệu phức tạp

  3.6.2 Ví dụ: Agent trả lời câu hỏi từ tài liệu
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    from llama_index.core.agent import ReActAgent
    from llama_index.core.tools import QueryEngineTool

    # Load và index tài liệu
    documents = SimpleDirectoryReader("./docs").load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()

    # Tạo tool từ query engine
    doc_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        description="Tìm kiếm thông tin trong tài liệu công ty"
    )

    agent = ReActAgent.from_tools([doc_tool], llm=llm, verbose=True)
    response = agent.chat("Chính sách nghỉ phép năm 2025 là gì?")

## 3.7 So sánh và lựa chọn framework

  Framework    | Điểm mạnh              | Use case tiêu biểu
  -------------|------------------------|------------------------
  LangChain    | Hệ sinh thái lớn       | Prototype, tích hợp nhanh
  LangGraph    | Kiểm soát luồng tốt    | Agent phức tạp, stateful
  CrewAI       | Multi-agent dễ dùng    | Workflow với nhiều vai trò
  AutoGen      | Agent chat, code exec  | Pair programming, debate
  LlamaIndex   | RAG chuyên sâu         | Q&A trên tài liệu lớn
  Agno         | Nhẹ, hiệu năng cao     | Production, scale

  Lộ trình học framework đề xuất:
    Tuần 1-2 : LangChain cơ bản (chains, tools, memory)
    Tuần 3-4 : LangGraph (stateful agent, human-in-the-loop)
    Tuần 5   : CrewAI (multi-agent workflow)
    Tuần 6   : LlamaIndex (RAG nâng cao)
    Tuần 7+  : Dự án kết hợp nhiều framework

## 3.8 Tools & Integrations quan trọng

  3.8.1 Search & Browsing
    - Tavily Search API  : tối ưu cho AI agent, có structured output
    - Brave Search API   : không cần credit card thử nghiệm
    - Playwright/Selenium: điều khiển trình duyệt

  3.8.2 Code Execution
    - E2B (e2b.dev)    : sandbox an toàn cho LLM chạy code
    - Modal            : serverless code execution
    - Docker sandbox   : tự host, kiểm soát hoàn toàn

  3.8.3 Data & APIs
    - Zapier / Make    : kết nối 1000+ app không cần code
    - Composio         : tool integrations cho AI agent
    - Browserbase      : cloud browser cho agent

## 3.9 Tóm tắt chương

  Frameworks theo mục đích:
    ✓ Bắt đầu học   → LangChain + LangGraph
    ✓ Multi-agent   → CrewAI
    ✓ Tài liệu/RAG  → LlamaIndex
    ✓ Code agent    → AutoGen

  Nguyên tắc quan trọng:
    → Học framework bằng cách XÂY DỰ ÁN, không chỉ đọc docs
    → Luôn hiểu "framework đang làm gì" ở tầng thấp hơn
    → Không cần học tất cả – chọn 1-2 và thành thạo

