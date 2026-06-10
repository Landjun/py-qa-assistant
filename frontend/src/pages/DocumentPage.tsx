import { useEffect, useRef, useState } from "react";
import {
  uploadDocument,
  listDocuments,
  getChunks,
  deleteDocument,
  type Document,
  type Chunk,
} from "../api/documents";

const STATUS_LABEL: Record<string, { text: string; cls: string }> = {
  ready: { text: "就绪", cls: "bg-green-100 text-green-700" },
  processing: { text: "处理中", cls: "bg-yellow-100 text-yellow-700" },
  error: { text: "错误", cls: "bg-red-100 text-red-700" },
};

function StatusBadge({ status }: { status: string }) {
  const s = STATUS_LABEL[status] ?? { text: status, cls: "bg-gray-100 text-gray-600" };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${s.cls}`}>
      {s.text}
    </span>
  );
}

// ─── 分块详情面板 ─────────────────────────────────────────────────────────────

function ChunkPanel({
  doc,
  onClose,
}: {
  doc: Document;
  onClose: () => void;
}) {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getChunks(doc.id)
      .then(setChunks)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "加载失败"))
      .finally(() => setLoading(false));
  }, [doc.id]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="flex h-[80vh] w-[700px] max-w-[95vw] flex-col rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
          <div>
            <p className="font-semibold text-gray-800">{doc.title}</p>
            <p className="text-xs text-gray-500">共 {doc.chunk_count} 个分块</p>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loading && <p className="text-sm text-gray-400">加载中…</p>}
          {error && <p className="text-sm text-red-500">{error}</p>}
          {chunks.map((chunk, i) => (
            <div key={chunk.id} className="rounded border border-gray-200 bg-gray-50 p-3">
              <div className="mb-1 flex items-center gap-2">
                <span className="text-xs font-semibold text-gray-400">#{i + 1}</span>
                <span className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600">
                  {chunk.title_path}
                </span>
                <span className="ml-auto text-xs text-gray-400">{chunk.char_count} 字</span>
              </div>
              <p className="whitespace-pre-wrap text-xs text-gray-700 leading-relaxed">
                {chunk.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── 主页面 ──────────────────────────────────────────────────────────────────

export default function DocumentPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function fetchDocs() {
    try {
      const list = await listDocuments();
      setDocuments(list);
    } catch {
      // 静默
    }
  }

  useEffect(() => { fetchDocs(); }, []);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.name.endsWith(".md") && !file.name.endsWith(".txt")) {
      setUploadError("只支持 .md / .txt 文件");
      return;
    }

    setUploading(true);
    setUploadError("");
    try {
      await uploadDocument(file);
      await fetchDocs();
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : "上传失败");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  async function handleDelete(doc: Document, e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm(`确认删除「${doc.title}」及其 ${doc.chunk_count} 个分块？`)) return;
    try {
      await deleteDocument(doc.id);
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id));
      if (selectedDoc?.id === doc.id) setSelectedDoc(null);
    } catch {
      alert("删除失败，请重试");
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleString("zh-CN", {
      month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit",
    });
  }

  return (
    <div className="flex h-full flex-col">
      <h1 className="mb-4 text-2xl font-semibold">文档管理</h1>

      {/* 上传区 */}
      <div className="mb-4 flex items-center gap-3">
        <label
          className={`cursor-pointer rounded border border-dashed border-blue-400 bg-blue-50 px-4 py-2 text-sm text-blue-600 hover:bg-blue-100 ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {uploading ? "上传中…" : "+ 上传 Markdown 文档"}
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.txt"
            className="hidden"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </label>
        <span className="text-xs text-gray-400">支持 .md / .txt，最大 5MB</span>
        {uploadError && (
          <span className="text-xs text-red-500">{uploadError}</span>
        )}
      </div>

      {/* 文档列表 */}
      {documents.length === 0 ? (
        <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
          <p className="text-sm text-gray-400">暂无文档，上传 Markdown 文件以构建知识库</p>
        </div>
      ) : (
        <div className="flex-1 overflow-auto rounded-lg border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 bg-gray-50 text-xs text-gray-500">
              <tr>
                <th className="px-4 py-2 text-left">文件名</th>
                <th className="px-4 py-2 text-left">状态</th>
                <th className="px-4 py-2 text-right">分块数</th>
                <th className="px-4 py-2 text-left">上传时间</th>
                <th className="px-4 py-2 text-center">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {doc.filename}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">
                    {doc.chunk_count}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {formatDate(doc.created_at)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => setSelectedDoc(doc)}
                      className="mr-2 rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50"
                    >
                      查看分块
                    </button>
                    <button
                      onClick={(e) => handleDelete(doc, e)}
                      className="rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 分块详情面板 */}
      {selectedDoc && (
        <ChunkPanel doc={selectedDoc} onClose={() => setSelectedDoc(null)} />
      )}
    </div>
  );
}
