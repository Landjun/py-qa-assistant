import { useEffect, useRef, useState, useCallback } from "react";
import { ask, type RAGAnswer, type BugDetail, type SourceInfo, type ImageUnderstanding } from "../api/chat";
import {
  listConversations,
  getMessages,
  deleteConversation,
  parseExtra,
  type Conversation,
  type Message,
} from "../api/conversations";
import { retrievalSearch, type RetrievalResult } from "../api/retrieval";
import { useAuthStore } from "../store/auth";

// ─── RAG 答案卡片 ─────────────────────────────────────────────────────────────

function SourcesPanel({ sources }: { sources: SourceInfo[] }) {
  if (sources.length === 0) {
    return <p className="text-xs italic text-gray-400">本次回答未引用知识库</p>;
  }
  return (
    <div className="rounded border border-indigo-100 bg-indigo-50 p-3">
      <p className="mb-2 text-xs font-semibold text-indigo-600">引用来源</p>
      <div className="space-y-1">
        {sources.map((s, i) => (
          <div key={i} className="flex items-center justify-between text-xs">
            <span className="truncate text-gray-700" title={s.source}>{s.source}</span>
            <span className="ml-2 shrink-0 text-gray-400">
              chunk:{s.chunk_id} · {(s.score * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImageBadge({ iu }: { iu: ImageUnderstanding }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5 rounded bg-purple-50 px-3 py-1.5 text-xs text-purple-700">
      <span>📷</span>
      <span className="font-medium">已识别图片：{iu.image_type}</span>
      {iu.detected_error && (
        <span className="rounded bg-purple-100 px-1.5 py-0.5 font-mono text-purple-800">
          {iu.detected_error}
        </span>
      )}
      {iu.summary && (
        <span className="text-purple-500">— {iu.summary}</span>
      )}
    </div>
  );
}

// ─── Bug 报错排查卡片 ─────────────────────────────────────────────────────────

function BugAnswerCard({
  bug,
  sources,
  durationMs,
}: {
  bug: BugDetail;
  sources: SourceInfo[];
  durationMs?: number;
}) {
  return (
    <div className="space-y-3 rounded-lg border border-red-100 bg-white p-4 text-sm shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-semibold text-red-700">
            报错排查
          </span>
          {bug.error_type && (
            <span className="rounded bg-gray-100 px-2 py-0.5 font-mono text-xs text-gray-700">
              {bug.error_type}
            </span>
          )}
        </div>
        {durationMs != null && (
          <span className="shrink-0 text-xs text-gray-400">{durationMs} ms</span>
        )}
      </div>

      {/* 大白话解释 */}
      {bug.plain_explanation && (
        <div className="rounded bg-amber-50 p-3">
          <p className="mb-1 text-xs font-semibold text-amber-600">大白话解释</p>
          <p className="text-gray-700">{bug.plain_explanation}</p>
        </div>
      )}

      {/* 可能原因 */}
      {bug.likely_causes.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-semibold text-gray-500">可能原因</p>
          <ul className="list-inside list-disc space-y-0.5 text-gray-700">
            {bug.likely_causes.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}

      {/* 修复步骤 */}
      {bug.fix_steps.length > 0 && (
        <div>
          <p className="mb-1 text-xs font-semibold text-gray-500">修复步骤</p>
          <ol className="list-inside list-decimal space-y-0.5 text-gray-700">
            {bug.fix_steps.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </div>
      )}

      {/* 修复前 / 修复后代码 */}
      {(bug.before_code || bug.after_code) && (
        <div className="grid gap-2 sm:grid-cols-2">
          {bug.before_code && (
            <div>
              <p className="mb-1 text-xs font-semibold text-red-500">修复前</p>
              <pre className="overflow-x-auto rounded bg-gray-900 p-3 text-xs text-red-300">
                <code>{bug.before_code}</code>
              </pre>
            </div>
          )}
          {bug.after_code && (
            <div>
              <p className="mb-1 text-xs font-semibold text-green-600">修复后</p>
              <pre className="overflow-x-auto rounded bg-gray-900 p-3 text-xs text-green-300">
                <code>{bug.after_code}</code>
              </pre>
            </div>
          )}
        </div>
      )}

      {/* 需要补充的信息 */}
      {bug.need_more_info && bug.need_more_info_fields.length > 0 && (
        <div className="rounded border border-orange-200 bg-orange-50 p-3">
          <p className="mb-1 text-xs font-semibold text-orange-600">还需要你补充：</p>
          <ul className="list-inside list-disc space-y-0.5 text-gray-700">
            {bug.need_more_info_fields.map((f, i) => <li key={i}>{f}</li>)}
          </ul>
        </div>
      )}

      {/* 来源 */}
      <SourcesPanel sources={sources} />
    </div>
  );
}


function RAGAnswerCard({
  answer,
  durationMs,
  intent,
}: {
  answer: RAGAnswer;
  durationMs?: number;
  intent?: string;
}) {
  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4 text-sm shadow-sm">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {intent && (
            <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${INTENT_COLOR[intent] ?? "bg-gray-100 text-gray-600"}`}>
              {INTENT_LABEL[intent] ?? intent}
            </span>
          )}
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              answer.useful ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
            }`}
          >
            {answer.useful ? "知识库匹配" : "知识库不足"}
          </span>
        </div>
        {durationMs != null && (
          <span className="text-xs text-gray-400 shrink-0">{durationMs} ms</span>
        )}
      </div>

      {answer.content && (
        <div>
          <p className="mb-1 text-xs font-semibold text-gray-500">回答</p>
          <p className="whitespace-pre-wrap text-gray-800">{answer.content}</p>
        </div>
      )}

      {answer.beginner_explanation && (
        <div className="rounded bg-amber-50 p-3">
          <p className="mb-1 text-xs font-semibold text-amber-600">大白话解释</p>
          <p className="whitespace-pre-wrap text-gray-700">{answer.beginner_explanation}</p>
        </div>
      )}

      {answer.code_example && (
        <div>
          <p className="mb-1 text-xs font-semibold text-gray-500">代码示例</p>
          <pre className="overflow-x-auto rounded bg-gray-900 p-3 text-xs text-green-300">
            <code>{answer.code_example}</code>
          </pre>
        </div>
      )}

      <SourcesPanel sources={answer.sources} />
    </div>
  );
}

// ─── 检索结果卡片 ─────────────────────────────────────────────────────────────

function RetrievalResultCard({ result, rank }: { result: RetrievalResult; rank: number }) {
  const scoreColor =
    result.score >= 0.8
      ? "bg-green-100 text-green-700"
      : result.score >= 0.65
      ? "bg-blue-100 text-blue-700"
      : "bg-gray-100 text-gray-600";
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm shadow-sm">
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
            {rank}
          </span>
          <span className="max-w-[200px] truncate font-medium text-gray-700" title={result.source}>
            {result.source}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${scoreColor}`}>
            {(result.score * 100).toFixed(1)}%
          </span>
          <span className="text-xs text-gray-400">
            doc:{result.document_id} · chunk:{result.chunk_id}
          </span>
        </div>
      </div>
      <p className="whitespace-pre-wrap leading-relaxed text-gray-700">{result.content}</p>
    </div>
  );
}

function RetrievalResultsBlock({
  query,
  results,
  durationMs,
}: {
  query: string;
  results: RetrievalResult[];
  durationMs: number;
}) {
  return (
    <div className="space-y-2 rounded-lg border border-indigo-100 bg-indigo-50 p-3">
      <div className="flex items-center justify-between text-xs text-indigo-600">
        <span className="font-semibold">检索结果 · "{query}"</span>
        <span>{results.length} 条 · {durationMs} ms</span>
      </div>
      {results.length === 0 ? (
        <p className="py-2 text-sm text-gray-500">未找到相关内容，请调整关键词或降低阈值。</p>
      ) : (
        <div className="space-y-2">
          {results.map((r, i) => (
            <RetrievalResultCard key={r.chunk_id} result={r} rank={i + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─── 消息类型 ─────────────────────────────────────────────────────────────────

const INTENT_LABEL: Record<string, string> = {
  PYTHON_QA: "Python 答疑",
  BUG_HELP: "报错排查",
  FEEDBACK: "系统反馈",
  CHAT: "闲聊",
};

const INTENT_COLOR: Record<string, string> = {
  PYTHON_QA: "bg-blue-100 text-blue-700",
  BUG_HELP: "bg-red-100 text-red-700",
  FEEDBACK: "bg-purple-100 text-purple-700",
  CHAT: "bg-gray-100 text-gray-600",
};

type UIMessage =
  | { role: "user"; text: string }
  | {
      role: "rag-assistant";
      answer: RAGAnswer;
      durationMs?: number;
      intent?: string;
      imageUnderstanding?: ImageUnderstanding;
    }
  | { role: "retrieval"; query: string; results: RetrievalResult[]; durationMs: number }
  | { role: "error"; text: string };

function historyToRAGAnswer(msg: Message): { answer: RAGAnswer; intent?: string } | null {
  const extra = parseExtra(msg);
  if (!extra || extra.type !== "rag") return null;
  return {
    answer: {
      useful: extra.useful ?? true,
      content: msg.content,
      beginner_explanation: extra.beginner_explanation ?? "",
      code_example: extra.code_example ?? "",
      sources: extra.sources ?? [],
      bug_detail: extra.bug_detail ?? undefined,
    },
    intent: extra.intent,
  };
}

function MessageItem({ msg }: { msg: UIMessage }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] rounded-lg bg-blue-600 px-4 py-2 text-sm text-white">
          {msg.text}
        </div>
      </div>
    );
  }
  if (msg.role === "rag-assistant") {
    return (
      <div className="flex justify-start">
        <div className="w-full max-w-[92%] space-y-1.5">
          {msg.imageUnderstanding && <ImageBadge iu={msg.imageUnderstanding} />}
          {msg.answer.bug_detail ? (
            <BugAnswerCard
              bug={msg.answer.bug_detail}
              sources={msg.answer.sources}
              durationMs={msg.durationMs}
            />
          ) : (
            <RAGAnswerCard answer={msg.answer} durationMs={msg.durationMs} intent={msg.intent} />
          )}
        </div>
      </div>
    );
  }
  if (msg.role === "retrieval") {
    return (
      <div className="flex justify-start">
        <div className="w-full max-w-[96%]">
          <RetrievalResultsBlock query={msg.query} results={msg.results} durationMs={msg.durationMs} />
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start">
      <div className="max-w-[70%] rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
        <span className="mr-1 font-semibold">错误：</span>{msg.text}
      </div>
    </div>
  );
}

// ─── 图片处理工具 ─────────────────────────────────────────────────────────────

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp"];

// ─── 主页面 ──────────────────────────────────────────────────────────────────

export default function ChatPage() {
  const user = useAuthStore((s) => s.user);
  const isStudent = user?.role === "student";

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [uiMessages, setUiMessages] = useState<UIMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [retrievalMode, setRetrievalMode] = useState(false);

  // 图片状态
  const [pendingImageBase64, setPendingImageBase64] = useState<string | null>(null);
  const [pendingImagePreview, setPendingImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchConversations = useCallback(async () => {
    try {
      setConversations(await listConversations());
    } catch {
      // 静默失败
    }
  }, []);

  useEffect(() => { fetchConversations(); }, [fetchConversations]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [uiMessages, loading]);

  // ─── 图片处理 ───────────────────────────────────────────────────────────────

  function processImageFile(file: File) {
    if (!ALLOWED_TYPES.includes(file.type)) {
      alert("仅支持 PNG / JPG / WebP 格式的图片");
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      alert(`图片大小 ${(file.size / 1024 / 1024).toFixed(1)}MB 超过 5MB 限制，请压缩后重试`);
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      setPendingImagePreview(dataUrl);
      setPendingImageBase64(dataUrl.split(",")[1]);
    };
    reader.readAsDataURL(file);
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) processImageFile(file);
    e.target.value = "";
  }

  function handlePaste(e: React.ClipboardEvent) {
    const items = Array.from(e.clipboardData.items);
    const imageItem = items.find((item) => item.type.startsWith("image/"));
    if (imageItem) {
      const file = imageItem.getAsFile();
      if (file) {
        e.preventDefault();
        processImageFile(file);
      }
    }
  }

  function clearImage() {
    setPendingImageBase64(null);
    setPendingImagePreview(null);
  }

  // ─── 会话操作 ───────────────────────────────────────────────────────────────

  async function selectConversation(conv: Conversation) {
    if (activeId === conv.id) return;
    setActiveId(conv.id);
    setUiMessages([]);
    setLoadingHistory(true);
    try {
      const msgs = await getMessages(conv.id);
      const ui: UIMessage[] = msgs.map((m) => {
        if (m.role === "user") return { role: "user", text: m.content };
        const extra = parseExtra(m);
        const parsed = historyToRAGAnswer(m);
        if (parsed) {
          return { role: "rag-assistant", answer: parsed.answer, intent: parsed.intent, durationMs: extra?.duration_ms };
        }
        return {
          role: "rag-assistant",
          answer: {
            useful: true,
            content: m.content,
            beginner_explanation: extra?.beginner_explanation ?? "",
            code_example: extra?.code_example ?? "",
            sources: [],
          },
          durationMs: extra?.duration_ms,
        };
      });
      setUiMessages(ui);
    } catch {
      setUiMessages([{ role: "error", text: "加载历史消息失败" }]);
    } finally {
      setLoadingHistory(false);
    }
  }

  function newConversation() {
    setActiveId(null);
    setUiMessages([]);
    setInput("");
    clearImage();
  }

  async function handleDelete(conv: Conversation, e: React.MouseEvent) {
    e.stopPropagation();
    try {
      await deleteConversation(conv.id);
      setConversations((prev) => prev.filter((c) => c.id !== conv.id));
      if (activeId === conv.id) { setActiveId(null); setUiMessages([]); }
    } catch {
      alert("删除失败，请重试");
    }
  }

  // ─── 发送 ────────────────────────────────────────────────────────────────────

  async function handleSend() {
    const q = input.trim();
    if (!q && !pendingImageBase64) return;
    if (loading) return;

    const userText = q || "（发送了一张图片）";
    setUiMessages((prev) => [...prev, { role: "user", text: userText }]);
    const imageToSend = pendingImageBase64;
    setInput("");
    clearImage();
    setLoading(true);

    if (retrievalMode) {
      try {
        const res = await retrievalSearch(q);
        setUiMessages((prev) => [
          ...prev,
          { role: "retrieval", query: q, results: res.results, durationMs: res.duration_ms },
        ]);
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "检索失败";
        setUiMessages((prev) => [...prev, { role: "error", text: msg }]);
      } finally {
        setLoading(false);
      }
      return;
    }

    // RAG 问答模式
    try {
      const res = await ask(q, activeId ?? undefined, imageToSend ?? undefined);
      if (res.conversation_id && res.conversation_id !== activeId) {
        setActiveId(res.conversation_id);
        await fetchConversations();
      }
      if (res.success && res.answer) {
        setUiMessages((prev) => [
          ...prev,
          {
            role: "rag-assistant",
            answer: res.answer!,
            durationMs: res.duration_ms,
            intent: res.intent || undefined,
            imageUnderstanding: res.image_understanding ?? undefined,
          },
        ]);
      } else {
        setUiMessages((prev) => [
          ...prev,
          { role: "error", text: res.error || "未知错误" },
        ]);
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "请求失败，请检查网络";
      setUiMessages((prev) => [...prev, { role: "error", text: msg }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  }

  // ─── 渲染 ───────────────────────────────────────────────────────────────────

  return (
    <div className="flex h-full gap-0 overflow-hidden">
      {/* 左侧会话列表（检索模式 / 学员模式隐藏） */}
      {!isStudent && !retrievalMode && (
        <aside className="flex w-52 shrink-0 flex-col border-r border-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-gray-100 px-3 py-3">
            <span className="text-xs font-semibold text-gray-500">会话列表</span>
            <button
              onClick={newConversation}
              className="rounded px-2 py-0.5 text-xs text-blue-600 hover:bg-blue-50"
            >
              + 新建
            </button>
          </div>
          <div className="flex-1 overflow-y-auto">
            {conversations.length === 0 ? (
              <p className="px-3 py-4 text-xs text-gray-400">暂无会话，发送第一条消息自动创建</p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => selectConversation(conv)}
                  className={`group flex cursor-pointer items-center justify-between px-3 py-2 text-sm ${
                    activeId === conv.id ? "bg-blue-50 text-blue-700" : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <span className="flex-1 truncate">{conv.title}</span>
                  <button
                    onClick={(e) => handleDelete(conv, e)}
                    className="ml-1 hidden shrink-0 text-gray-400 hover:text-red-500 group-hover:block"
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>
      )}

      {/* 右侧消息区 */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* 模式切换栏（学员模式隐藏） */}
        {!isStudent && (
          <div className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-2">
            <span className="text-xs text-gray-500">
              {retrievalMode
                ? "检索测试模式 — 直接返回知识库匹配片段"
                : "RAG 问答模式 — 知识库检索 + DeepSeek 智能答疑"}
            </span>
            <label className="flex cursor-pointer select-none items-center gap-2">
              <span className="text-xs font-medium text-gray-600">检索测试模式</span>
              <div className="relative">
                <input
                  type="checkbox"
                  className="sr-only"
                  checked={retrievalMode}
                  onChange={(e) => { setRetrievalMode(e.target.checked); setUiMessages([]); }}
                />
                <div className={`h-5 w-9 rounded-full transition-colors ${retrievalMode ? "bg-indigo-600" : "bg-gray-300"}`} />
                <div className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${retrievalMode ? "translate-x-4" : "translate-x-0"}`} />
              </div>
            </label>
          </div>
        )}

        {/* 消息列表 */}
        <div className="flex-1 space-y-4 overflow-y-auto bg-gray-50 p-4">
          {loadingHistory ? (
            <p className="mt-8 text-center text-sm text-gray-400">加载历史消息…</p>
          ) : uiMessages.length === 0 ? (
            <p className="mt-12 text-center text-sm text-gray-400">
              {retrievalMode
                ? "输入关键词，检索知识库中最相关的片段"
                : isStudent
                ? "有什么 Python 问题？随时问我 🐍"
                : "开始一个 Python 学习问题吧 🐍"}
            </p>
          ) : (
            uiMessages.map((msg, i) => <MessageItem key={i} msg={msg} />)
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-400 shadow-sm">
                <span className="animate-pulse">
                  {retrievalMode ? "检索中…" : "知识库检索 + DeepSeek 答疑中…"}
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* 输入区 */}
        <div className="border-t border-gray-200 bg-white px-4 py-3">
          {/* 图片预览缩略图 */}
          {pendingImagePreview && (
            <div className="mb-2 flex items-center gap-2">
              <div className="relative">
                <img
                  src={pendingImagePreview}
                  alt="待发送图片"
                  className="h-16 w-16 rounded border border-gray-200 object-cover"
                />
                <button
                  onClick={clearImage}
                  className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-gray-600 text-[10px] text-white hover:bg-red-500"
                >
                  ✕
                </button>
              </div>
              <span className="text-xs text-gray-400">图片已选，发送时一起提交</span>
            </div>
          )}

          <div className="flex gap-2" onPaste={handlePaste}>
            {/* 隐藏文件输入 */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp"
              className="hidden"
              onChange={handleFileChange}
            />
            {/* 图片上传按钮 */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              title="上传图片（支持 PNG / JPG / WebP，可粘贴截图）"
              className={`flex h-9 w-9 shrink-0 items-center justify-center rounded border text-base transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
                pendingImagePreview
                  ? "border-purple-400 bg-purple-50 text-purple-600"
                  : "border-gray-300 bg-white text-gray-500 hover:border-blue-400 hover:text-blue-500"
              }`}
            >
              📷
            </button>
            <input
              className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm outline-none focus:border-blue-500 disabled:bg-gray-50"
              placeholder={
                retrievalMode
                  ? "输入检索关键词，Enter 检索…"
                  : pendingImagePreview
                  ? "可补充文字说明（可留空直接发送）…"
                  : "输入 Python 问题，或粘贴截图，Enter 发送…"
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={(!input.trim() && !pendingImageBase64) || loading}
              className={`rounded px-4 py-2 text-sm text-white disabled:cursor-not-allowed disabled:opacity-50 ${
                retrievalMode ? "bg-indigo-600 hover:bg-indigo-700" : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {loading
                ? (retrievalMode ? "检索中…" : "答疑中…")
                : (retrievalMode ? "检索" : "发送")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
