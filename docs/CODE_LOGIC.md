# 代码逻辑梳理

本文档描述从前端到后端、Agent、工具与数据的完整数据流与逻辑。

---

## 1. 整体架构

```
用户浏览器 (Vite 前端)
    ↓ POST /api/agent  (Vite proxy → 后端 PORT)
Flask API (api/app.py)
    ↓ run_agent(question)
Agent (router → run_plan → synthesizer)
    ↓ 使用 LLM + RAG + platform_chooser
返回 { reply, raw } → 前端展示
```

---

## 2. 前端 (frontend/src/App.jsx)

### 2.1 入口与状态

- **IntroScreen**：首次访问显示 2.8 秒开场，或点 "Enter" 跳过；`localStorage` 存 `eecs6895_intro_seen`，之后不再显示。
- **三步问卷**：依次收集 **Ad Info**、**Budget**、**Target Audience**，存在 state：`adInfo`、`budget`、`targetAudience`。
- **step**：0 → 1 → 2 → 3。step 0/1/2 时只展示当前问题并等待输入；step 3 表示三步已填完，可发起请求。
- **loading / error / reply**：请求中、错误信息、后端回复文案。

### 2.2 发送逻辑 (sendInput)

1. **step 0**：用户输入 → 存为 `adInfo`，`step` 设为 1。
2. **step 1**：用户输入 → 存为 `budget`，`step` 设为 2。
3. **step 2**：用户输入 → 存为 `targetAudience`，`step` 设为 3，并**发起请求**：
   - 拼接 `message = "Ad Info: {adInfo}\nBudget: {budget}\nTarget Audience: {targetAudience}"`。
   - **POST /api/agent**，body：`{ question: message }`。
   - 成功：`setReply(data.reply)`。
   - 失败：`setError(err.message)`。
   - 最后 `setLoading(false)`。

### 2.3 展示

- 按 step 展示三道题与用户已填内容。
- `loading` 时显示 typing 动画。
- `hasReply = (reply 非空)` 时展示「Response」块：`reply` 文案。
- 有 reply 后输入框禁用，提示 "Start over by refreshing the page."

### 2.4 网络

- 开发时 Vite 将 **/api** 代理到 `http://127.0.0.1:${VITE_BACKEND_PORT || 9999}`，因此前端请求 **/api/agent** 会打到后端的 **/api/agent**。

---

## 3. 后端 API (api/app.py)

### 3.1 路由

| 路径 | 方法 | 作用 |
|------|------|------|
| /health | GET | 健康检查，返回 `{ "status": "ok" }` |
| /agent | POST | 直接返回 `run_agent(question)` 的完整结果（供调试等） |
| **/api/agent** | POST | **前端使用**：入参 `{ question }`，返回 `{ reply, raw }` |
| /api/advice-chat | POST | 纯 LLM 对话：入参 `{ messages }`，返回 `{ reply [, assign_time_ms ] }`（当前前端未用） |

### 3.2 /api/agent 逻辑

1. 从 body 取 `question`，空则 400。
2. 调用 `run_agent(question)`，得到 `result`。
3. `reply = result["final_answer"]`。
4. 返回 `{ reply, raw: result }`；异常时 500 并返回 `{ error }`。

### 3.3 启动

- `python api/app.py` 时，`PORT = os.environ.get("PORT", 9999)`，默认 **9999**，与前端代理一致。

---

## 4. Agent 流程 (src/marketing_agent/agent/run.py)

### 4.1 run_agent(question)

1. **LLM**：`llm = get_llm()`（由 config.LLM_BACKEND 决定，openai / huggingface）。
2. **Retriever**：若未传入则用 `_get_default_retriever()`：
   - 若存在 `config.CORPUS_PATH`，则 `load_jsonl_corpus` → `build_vectorstore` → `get_retriever`（embed 模型用 `config.EMBED_MODEL_NAME`，top-k 用 `config.RAG_TOP_K`）。
3. **工具注册表**：`platform_chooser` 必选；若 retriever 存在则注册 `rag`（由 `make_tool_rag(retriever, llm)` 生成）。
4. **路由**：`plan = route_question(question, llm)`，得到执行计划。
5. **执行**：`trace = run_plan(plan, tool_registry)`，按顺序执行每一步，得到 trace。
6. **合成**：`final_answer = synthesize_answer(question, trace, llm)`，用 LLM 把 trace 整理成最终回复。
7. 返回 `{ question, plan, trace, final_answer }`。

---

## 5. 路由 (router.py + prompts/router.py)

### 5.1 职责

根据用户问题生成**执行计划**：`{ "plan": [ { "tool", "args" }, ... ] }`。  
当前只支持两种工具：**platform_chooser**（1 步）、**rag**（2～5 步）。

### 5.2 流程

1. 用 **prompts.router** 的 `make_router_prompt(question)` 生成 prompt，要求 LLM 输出 JSON：
   - 1 个 `platform_chooser`：args 含 `industry`（从问题推断）、`region`（默认 US）、`include_audience`。
   - 2～5 个 `rag`：每个不同的 policy/平台问题，`question` + `k`（默认 3）。
2. LLM 生成 → `extract_json` 解析。
3. ** _cap_rag_steps**：只保留 1 个 platform_chooser + 最多 `MAX_RAG_STEPS`（默认 5）个 rag，多余 rag 丢弃。
4. 若解析失败或 schema 不对：使用 ** _fallback_plan(question)**：固定 1 个 platform_chooser + 3 个 rag（Meta / Google / TikTok policy）。

---

## 6. 执行计划 (tools/registry.py run_plan)

- 遍历 `plan["plan"]` 中每一步。
- 每步：`tool_name`、`args`；若 `tool_name` 不在 `tool_registry` 则记一条 error 进 trace 并 continue。
- 否则执行 `tool_registry[tool_name](**args)`，将 `{ tool, args, result, result_preview }` 追加到 trace。
- 工具抛异常时，result 记为 `{ "error": "..." }`，不中断后续步骤。

---

## 7. 工具

### 7.1 platform_chooser (tools/platform_chooser.py)

- **入参**：`industry`、`region`（默认 "US"）、`include_audience`（默认 True）。
- **逻辑**：从 **data/benchmarks** 下 CSV 读取：
  - Meta_2024Q3_By_Industry.csv、Google_Ads_2025_By_Industry.csv；
  - CPC_CPM_CPA_US_Only 或 Global、Audience_Behavior US/Global；
  - 按 industry、region 过滤，合并去重。
- **返回**：`{ status, message, industry_query, region, platforms: [...], audience: [...] }`，每项含 CPC/CPM/CPA、CTR、转化率、年龄分布、意图等字段。  
  若目录不存在则返回 `status: "error"`。

### 7.2 rag (tools/rag_tool.py → rag/pipeline.py)

- **入参**：`question`、`k`（默认 3）。
- **逻辑**：`rag_answer(question, retriever, llm, k, show_evidence=True)`：
  - `retriever.invoke(question)` 得到 top-k 文档；
  - 可选打印 evidence（调试）；
  - `build_rag_messages(docs, question)` 拼 context + 问题，用 **prompts.rag_system** 的 RAG_SYSTEM；
  - `llm.generate(messages)` 得到答案；
  - 构造 `evidence: [ { doc_id, title, ... } ]`。
- **返回**：`{ answer, evidence }`（synthesizer 里会从 evidence 抽 doc_id 做 citation）。

---

## 8. 合成 (synthesizer.py + prompts/ad_plan_synthesis.py)

### 8.1 职责

把 **trace**（platform_chooser 结果 + 多段 RAG 结果）用 LLM 整理成一篇**结构化广告计划**，作为 `final_answer`。

### 8.2 流程

1. **RAG 引用**：从 trace 里所有 `tool=="rag"` 的 result 中收集 `evidence[].doc_id`，去重得到 `citations`。
2. **拼工具输出**：把每条 trace 的 tool、args、result（截断到 2000 字符）拼成一大段文本。
3. **系统提示**：`get_ad_plan_synthesis_system(citations)`（来自 prompts.ad_plan_synthesis）：
   - 要求只使用工具输出、不编造数字；
   - 要求按 1. Platform Selection 2. Budget Allocation 3. Target Audience 4. Ad Formats 5. Key Compliance Points 6. Execution Recommendations 输出 Markdown；
   - 若有用到 RAG，必须带 [doc_id] 引用。
4. **用户消息**：问题 + 上述工具输出文本 + "Write the final answer:"。
5. LLM 生成（max_new_tokens 至少 1024，temperature=0.2）。
6. 若存在 citations 但回答里没有引用格式，则在文末追加 `Sources: [第一个 doc_id]`。

---

## 9. 配置 (config.py)

- **.env**：通过 `load_dotenv` 加载项目根目录 `.env`。
- **HF_HOME**：若未设置则设为 `项目根/data/.cache/huggingface`，避免权限问题。
- **LLM**：`LLM_BACKEND`（openai / huggingface）、OpenAI 的 API key/base URL/model、HuggingFace 的 token/model。
- **RAG**：`CORPUS_PATH`（JSONL 语料）、`EMBED_MODEL_NAME`、`RAG_TOP_K`。
- **Benchmarks**：`BENCHMARKS_DIR` 指向 `data/benchmarks`（platform_chooser 用）。

---

## 10. 数据流小结（从前端到回复）

1. 用户在前端完成三步 → 拼成一条 `question` 字符串。
2. 前端 **POST /api/agent** `{ question }`。
3. Flask **/api/agent** 调用 **run_agent(question)**。
4. **route_question** 用 LLM 生成 plan：1× platform_chooser + 2～5× rag。
5. **run_plan** 依次执行：  
   platform_chooser → 读 CSV 返回平台与受众数据；  
   每个 rag → 检索语料 + LLM 生成带 evidence 的答案。
6. **synthesize_answer** 把整条 trace 交给 LLM，按 ad_plan_synthesis 要求生成结构化 Markdown 文案，并补 RAG 引用。
7. **run_agent** 返回 `final_answer`，Flask 将其作为 **reply** 返回前端。
8. 前端展示 **reply**。

---

## 11. 关键文件索引

| 层级 | 文件 | 作用 |
|------|------|------|
| 前端 | frontend/src/App.jsx | 三步问卷、调用 /api/agent、展示 reply/图 |
| API | api/app.py | /health, /agent, /api/agent, /api/advice-chat |
| Agent | src/marketing_agent/agent/run.py | run_agent：路由 → 执行 → 合成 |
| 路由 | src/marketing_agent/agent/router.py | route_question：LLM 生成 plan |
| 执行 | src/marketing_agent/tools/registry.py | run_plan：按 plan 调工具 |
| 工具 | src/marketing_agent/tools/platform_chooser.py | 平台/受众基准数据 |
| 工具 | src/marketing_agent/tools/rag_tool.py + rag/pipeline.py | RAG 检索 + 生成带 evidence 的答案 |
| 合成 | src/marketing_agent/agent/synthesizer.py | 将 trace 合成为 final_answer |
| 配置 | src/marketing_agent/config.py | .env、LLM、RAG、benchmarks 路径 |
| 提示 | prompts/router.py | 路由 JSON 格式与规则 |
| 提示 | prompts/ad_plan_synthesis.py | 最终广告计划 Markdown 结构与引用规则 |
| 数据 | data/corpus/*.jsonl | RAG 语料 |
| 数据 | data/benchmarks/*.csv | platform_chooser 使用的 CSV |
