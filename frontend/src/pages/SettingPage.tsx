import { useEffect, useState } from "react";
import { getSystemStatus, SystemStatus } from "../api/settings";

function StatusRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <tr className="border-b last:border-b-0">
      <td className="py-3 pr-8 text-sm font-medium text-gray-600 whitespace-nowrap">{label}</td>
      <td className="py-3 text-sm text-gray-900">{value}</td>
    </tr>
  );
}

function Badge({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        ok ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`} />
      {ok ? "已配置" : "未配置"}
    </span>
  );
}

export default function SettingPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSystemStatus();
      setStatus(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "请求失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">系统设置</h1>
        <button
          onClick={load}
          disabled={loading}
          className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 disabled:opacity-50"
        >
          {loading ? "刷新中…" : "刷新"}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && !status && (
        <div className="text-sm text-gray-500">加载中…</div>
      )}

      {status && (
        <div className="space-y-6">
          {/* 知识库统计 */}
          <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-gray-800">知识库统计</h2>
            <table className="w-full">
              <tbody>
                <StatusRow label="文档数量" value={`${status.document_count} 个`} />
                <StatusRow label="分块数量" value={`${status.chunk_count} 个`} />
                <StatusRow
                  label="FAISS 向量数"
                  value={
                    <span className="font-mono font-semibold text-indigo-600">
                      {status.faiss_vector_count}
                    </span>
                  }
                />
              </tbody>
            </table>
          </section>

          {/* API 配置状态 */}
          <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-gray-800">API 配置状态</h2>
            <table className="w-full">
              <tbody>
                <StatusRow label="DeepSeek API Key" value={<Badge ok={status.deepseek_configured} />} />
                <StatusRow label="DashScope API Key" value={<Badge ok={status.dashscope_configured} />} />
              </tbody>
            </table>
          </section>

          {/* 模型信息 */}
          <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-gray-800">当前模型配置</h2>
            <table className="w-full">
              <tbody>
                <StatusRow
                  label="对话模型"
                  value={<span className="font-mono text-sm">{status.deepseek_model}</span>}
                />
                <StatusRow
                  label="嵌入模型"
                  value={<span className="font-mono text-sm">{status.embedding_model}</span>}
                />
                <StatusRow
                  label="重排模型"
                  value={<span className="font-mono text-sm">{status.rerank_model}</span>}
                />
              </tbody>
            </table>
          </section>
        </div>
      )}
    </div>
  );
}
