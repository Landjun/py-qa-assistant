import { useEffect, useState } from "react";
import { getLog, listLogs, LogDetail, LogItem, LogStep } from "../api/logs";

const INTENTS = ["PYTHON_QA", "BUG_HELP", "FEEDBACK", "CHAT"];

const intentColors: Record<string, string> = {
  PYTHON_QA: "bg-blue-100 text-blue-700",
  BUG_HELP: "bg-orange-100 text-orange-700",
  FEEDBACK: "bg-purple-100 text-purple-700",
  CHAT: "bg-gray-100 text-gray-600",
};

function StatusBadge({ status }: { status: string }) {
  const cls = status === "SUCCESS"
    ? "bg-green-100 text-green-700"
    : "bg-red-100 text-red-700";
  return <span className={`rounded px-2 py-0.5 text-xs font-medium ${cls}`}>{status}</span>;
}

function IntentBadge({ intent }: { intent: string }) {
  const cls = intentColors[intent] ?? "bg-gray-100 text-gray-600";
  return <span className={`rounded px-2 py-0.5 text-xs font-medium ${cls}`}>{intent || "—"}</span>;
}

function formatJson(raw: string): string {
  try {
    return JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    return raw;
  }
}

function StepCard({ step }: { step: LogStep }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded border border-gray-200 bg-white">
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-3">
          <span className="w-32 truncate font-mono text-sm font-medium text-gray-800">
            {step.step_name}
          </span>
          <span className="text-xs text-gray-400">{step.service_name}</span>
          <StatusBadge status={step.status} />
          {step.error_message && (
            <span className="max-w-xs truncate text-xs text-red-500">{step.error_message}</span>
          )}
        </div>
        <span className="text-xs text-gray-400">{step.duration_ms} ms {open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="grid grid-cols-2 gap-4 border-t border-gray-100 p-4">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Input</p>
            <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs text-gray-700">
              {formatJson(step.input_json)}
            </pre>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Output</p>
            <pre className="overflow-auto rounded bg-gray-50 p-3 text-xs text-gray-700">
              {formatJson(step.output_json)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function DetailView({ logId, onBack }: { logId: number; onBack: () => void }) {
  const [detail, setDetail] = useState<LogDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    getLog(logId)
      .then(setDetail)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [logId]);

  if (loading) return <div className="py-8 text-center text-gray-400">加载中…</div>;
  if (error) return <div className="py-8 text-center text-red-500">{error}</div>;
  if (!detail) return null;

  return (
    <div>
      <button
        className="mb-4 flex items-center gap-1 text-sm text-blue-600 hover:underline"
        onClick={onBack}
      >
        ← 返回列表
      </button>

      {/* Header */}
      <div className="mb-4 rounded-lg border border-gray-200 bg-white p-4">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="text-xs text-gray-400">#{detail.id}</span>
          <IntentBadge intent={detail.intent} />
          <StatusBadge status={detail.status} />
          <span className="text-xs text-gray-400">{detail.total_duration_ms} ms</span>
          <span className="text-xs text-gray-400">{detail.source_count} 个来源</span>
          <span className="ml-auto text-xs text-gray-400">
            {new Date(detail.created_at).toLocaleString("zh-CN")}
          </span>
        </div>
        <p className="mb-1 text-sm font-semibold text-gray-700">原始问题</p>
        <p className="mb-3 text-sm text-gray-800">{detail.question}</p>
        {detail.resolved_question !== detail.question && (
          <>
            <p className="mb-1 text-sm font-semibold text-gray-700">消解后问题</p>
            <p className="text-sm text-gray-600">{detail.resolved_question}</p>
          </>
        )}
      </div>

      {/* Final answer */}
      {detail.final_answer && (
        <div className="mb-4 rounded-lg border border-gray-200 bg-white p-4">
          <p className="mb-2 text-sm font-semibold text-gray-700">最终回答</p>
          <p className="whitespace-pre-wrap text-sm text-gray-700">{detail.final_answer}</p>
        </div>
      )}

      {/* Steps */}
      <div>
        <p className="mb-2 text-sm font-semibold text-gray-700">
          执行链路（{detail.steps.length} 步）
        </p>
        <div className="flex flex-col gap-2">
          {detail.steps.length === 0 ? (
            <p className="text-sm text-gray-400">无步骤记录</p>
          ) : (
            detail.steps.map((step) => <StepCard key={step.id} step={step} />)
          )}
        </div>
      </div>
    </div>
  );
}

export default function LogPage() {
  const [keyword, setKeyword] = useState("");
  const [intentFilter, setIntentFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<LogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const pageSize = 20;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const fetchLogs = (p = page) => {
    setLoading(true);
    listLogs({
      keyword: keyword || undefined,
      intent: intentFilter || undefined,
      status: statusFilter || undefined,
      page: p,
      page_size: pageSize,
    })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = () => {
    setPage(1);
    fetchLogs(1);
  };

  const handlePage = (p: number) => {
    setPage(p);
    fetchLogs(p);
  };

  if (selectedId !== null) {
    return (
      <div className="mx-auto max-w-4xl">
        <DetailView logId={selectedId} onBack={() => setSelectedId(null)} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="mb-4 text-2xl font-semibold">问答日志</h1>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <input
          type="text"
          placeholder="关键词搜索"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <select
          value={intentFilter}
          onChange={(e) => setIntentFilter(e.target.value)}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">全部意图</option>
          {INTENTS.map((i) => (
            <option key={i} value={i}>{i}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">全部状态</option>
          <option value="SUCCESS">SUCCESS</option>
          <option value="FAILED">FAILED</option>
        </select>
        <button
          onClick={handleSearch}
          className="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          搜索
        </button>
        <span className="text-sm text-gray-400">共 {total} 条</span>
      </div>

      {/* List */}
      {loading ? (
        <div className="py-8 text-center text-gray-400">加载中…</div>
      ) : items.length === 0 ? (
        <div className="py-8 text-center text-gray-400">暂无日志记录</div>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className="rounded-lg border border-gray-200 bg-white p-4 text-left transition hover:border-blue-400 hover:shadow-sm"
            >
              <div className="mb-1 flex flex-wrap items-center gap-2">
                <span className="text-xs text-gray-400">#{item.id}</span>
                <IntentBadge intent={item.intent} />
                <StatusBadge status={item.status} />
                <span className="text-xs text-gray-400">{item.total_duration_ms} ms</span>
                <span className="text-xs text-gray-400">{item.source_count} 个来源</span>
                <span className="ml-auto text-xs text-gray-400">
                  {new Date(item.created_at).toLocaleString("zh-CN")}
                </span>
              </div>
              <p className="truncate text-sm text-gray-800">{item.question}</p>
            </button>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-2">
          <button
            disabled={page <= 1}
            onClick={() => handlePage(page - 1)}
            className="rounded border px-3 py-1 text-sm disabled:opacity-40"
          >
            上一页
          </button>
          <span className="text-sm text-gray-500">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => handlePage(page + 1)}
            className="rounded border px-3 py-1 text-sm disabled:opacity-40"
          >
            下一页
          </button>
        </div>
      )}
    </div>
  );
}
