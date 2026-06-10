import { useCallback, useEffect, useRef, useState } from "react";
import {
  listCourses,
  listLessons,
  listAssets,
  uploadAsset,
  deleteAsset,
  updateLesson,
  init48,
  assetUrl,
  fmtBytes,
  type Course,
  type Lesson,
  type LessonAsset,
} from "../api/courses";
import { useAuthStore } from "../store/auth";

// ─── 资产类型图标 ─────────────────────────────────────────────────────────────
const ASSET_ICON: Record<string, string> = {
  slide: "📄",
  code: "🐍",
  other: "📦",
};

// ─── 工具 ─────────────────────────────────────────────────────────────────────
function badge(type: string) {
  const cls =
    type === "slide"
      ? "bg-blue-100 text-blue-700"
      : type === "code"
      ? "bg-green-100 text-green-700"
      : "bg-gray-100 text-gray-600";
  const label = type === "slide" ? "课件" : type === "code" ? "代码" : "其他";
  return (
    <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${cls}`}>{label}</span>
  );
}

// ─── 单节资源面板 ─────────────────────────────────────────────────────────────
function AssetPanel({
  lesson,
  isAdmin,
  onClose,
}: {
  lesson: Lesson;
  isAdmin: boolean;
  onClose: () => void;
}) {
  const [assets, setAssets] = useState<LessonAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadPct, setUploadPct] = useState(0);
  const [editTitle, setEditTitle] = useState(lesson.title);
  const [editSummary, setEditSummary] = useState(lesson.summary ?? "");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState("");
  const slideRef = useRef<HTMLInputElement>(null);
  const codeRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setAssets(await listAssets(lesson.id));
    } catch {
      setErr("加载资源失败");
    } finally {
      setLoading(false);
    }
  }, [lesson.id]);

  useEffect(() => { load(); }, [load]);

  async function handleUpload(file: File) {
    setUploading(true);
    setUploadPct(0);
    setErr("");
    try {
      const asset = await uploadAsset(lesson.id, file, setUploadPct);
      setAssets((prev) => [...prev, asset]);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "上传失败");
    } finally {
      setUploading(false);
      setUploadPct(0);
    }
  }

  async function handleDelete(assetId: number) {
    if (!confirm("确认删除该资源？")) return;
    try {
      await deleteAsset(assetId);
      setAssets((prev) => prev.filter((a) => a.id !== assetId));
    } catch {
      setErr("删除失败");
    }
  }

  async function handleSave() {
    setSaving(true);
    try {
      await updateLesson(lesson.id, { title: editTitle, summary: editSummary || null });
    } catch {
      setErr("保存失败");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
          <div>
            <p className="text-sm font-semibold text-gray-800">
              第 {lesson.lesson_no} 节
            </p>
            {isAdmin ? (
              <input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="mt-0.5 w-72 rounded border border-gray-300 px-2 py-1 text-sm focus:border-blue-500 focus:outline-none"
              />
            ) : (
              <p className="mt-0.5 text-base font-semibold text-gray-900">{lesson.title}</p>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">✕</button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* 知识点摘要 */}
          <div>
            <p className="mb-1 text-xs font-semibold text-gray-500">知识点摘要</p>
            {isAdmin ? (
              <textarea
                value={editSummary}
                onChange={(e) => setEditSummary(e.target.value)}
                rows={3}
                placeholder="本节涉及的主要知识点…"
                className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none resize-none"
              />
            ) : (
              <p className="text-sm text-gray-600 whitespace-pre-wrap">
                {lesson.summary || "（暂无摘要）"}
              </p>
            )}
          </div>

          {/* 资源列表 */}
          <div>
            <p className="mb-2 text-xs font-semibold text-gray-500">课节资源</p>
            {loading ? (
              <p className="text-sm text-gray-400">加载中…</p>
            ) : assets.length === 0 ? (
              <p className="text-sm text-gray-400">暂无资源</p>
            ) : (
              <div className="space-y-1.5">
                {assets.map((a) => (
                  <div
                    key={a.id}
                    className="flex items-center justify-between rounded border border-gray-200 bg-gray-50 px-3 py-2"
                  >
                    <div className="flex min-w-0 items-center gap-2">
                      <span>{ASSET_ICON[a.asset_type] ?? "📎"}</span>
                      {badge(a.asset_type)}
                      <a
                        href={assetUrl(a)}
                        download={a.filename}
                        target="_blank"
                        rel="noreferrer"
                        className="truncate text-sm text-blue-600 hover:underline"
                        title={a.filename}
                      >
                        {a.filename}
                      </a>
                      <span className="shrink-0 text-xs text-gray-400">{fmtBytes(a.size_bytes)}</span>
                    </div>
                    {isAdmin && (
                      <button
                        onClick={() => handleDelete(a.id)}
                        className="ml-2 shrink-0 text-xs text-red-400 hover:text-red-600"
                      >
                        删除
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {err && <p className="text-sm text-red-500">{err}</p>}

          {/* 上传按钮（admin only） */}
          {isAdmin && (
            <div className="flex gap-3">
              <input
                ref={slideRef}
                type="file"
                accept=".pdf,.ppt,.pptx"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); e.target.value = ""; }}
              />
              <input
                ref={codeRef}
                type="file"
                accept=".py,.ipynb,.txt,.zip"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); e.target.value = ""; }}
              />
              <button
                onClick={() => slideRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-1.5 rounded border border-blue-300 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 disabled:opacity-50"
              >
                📄 上传课件
              </button>
              <button
                onClick={() => codeRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-1.5 rounded border border-green-300 px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 disabled:opacity-50"
              >
                🐍 上传代码
              </button>
              {uploading && (
                <span className="self-center text-sm text-gray-500">
                  上传中 {uploadPct}%…
                </span>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {isAdmin && (
          <div className="flex items-center justify-end gap-3 border-t border-gray-200 px-5 py-3">
            <button onClick={onClose} className="text-sm text-gray-500 hover:text-gray-700">取消</button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="rounded bg-blue-600 px-4 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "保存中…" : "保存课节信息"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── 主页面 ──────────────────────────────────────────────────────────────────
export default function CoursePage() {
  const role = useAuthStore((s) => s.user?.role ?? "student");
  const isAdmin = role === "admin";

  const [course, setCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [initing, setIniting] = useState(false);
  const [activeLessonId, setActiveLessonId] = useState<number | null>(null);
  const [err, setErr] = useState("");

  const [assetCounts, setAssetCounts] = useState<Record<number, { slides: number; codes: number }>>({});

  const loadCourse = useCallback(async () => {
    setLoading(true);
    setErr("");
    try {
      const courses = await listCourses();
      if (courses.length === 0) {
        setCourse(null);
        setLessons([]);
        return;
      }
      const c = courses[0];
      setCourse(c);
      const ls = await listLessons(c.id);
      setLessons(ls);
      // 批量加载资源计数（并发）
      const counts: Record<number, { slides: number; codes: number }> = {};
      await Promise.all(
        ls.map(async (l) => {
          const assets = await listAssets(l.id);
          counts[l.id] = {
            slides: assets.filter((a) => a.asset_type === "slide").length,
            codes: assets.filter((a) => a.asset_type === "code").length,
          };
        })
      );
      setAssetCounts(counts);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadCourse(); }, [loadCourse]);

  async function handleInit() {
    setIniting(true);
    setErr("");
    try {
      await init48();
      await loadCourse();
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "初始化失败");
    } finally {
      setIniting(false);
    }
  }

  // 关闭弹窗后刷新该课节的资源计数
  async function handleClose(lessonId: number) {
    setActiveLessonId(null);
    try {
      const assets = await listAssets(lessonId);
      setAssetCounts((prev) => ({
        ...prev,
        [lessonId]: {
          slides: assets.filter((a) => a.asset_type === "slide").length,
          codes: assets.filter((a) => a.asset_type === "code").length,
        },
      }));
    } catch { /* ignore */ }
  }

  const activeLesson = activeLessonId !== null
    ? lessons.find((l) => l.id === activeLessonId) ?? null
    : null;

  // ─── 渲染 ────────────────────────────────────────────────────────────────────

  if (loading) {
    return <div className="p-8 text-sm text-gray-400">加载中…</div>;
  }

  if (!course) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24">
        <p className="text-base text-gray-500">尚未创建课程</p>
        {isAdmin && (
          <button
            onClick={handleInit}
            disabled={initing}
            className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {initing ? "初始化中…" : "一键初始化（1 门课 + 48 节）"}
          </button>
        )}
        {err && <p className="text-sm text-red-500">{err}</p>}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* 页面头 */}
      <div className="shrink-0 border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-gray-800">{course.name}</h2>
          <p className="text-xs text-gray-400 mt-0.5">{lessons.length} 个课节</p>
        </div>
        {isAdmin && (
          <button
            onClick={handleInit}
            disabled={initing}
            className="rounded border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50 disabled:opacity-50"
          >
            {initing ? "处理中…" : "重置 / 补全 48 节"}
          </button>
        )}
      </div>

      {err && <p className="shrink-0 px-6 py-2 text-sm text-red-500">{err}</p>}

      {/* 课节表格 */}
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 w-12">#</th>
              <th className="px-4 py-2.5 text-left text-xs font-medium text-gray-500">课节标题</th>
              <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 w-20">课件</th>
              <th className="px-4 py-2.5 text-center text-xs font-medium text-gray-500 w-20">代码</th>
              <th className="px-4 py-2.5 text-right text-xs font-medium text-gray-500 w-24">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {lessons.map((lesson) => {
              const cnt = assetCounts[lesson.id] ?? { slides: 0, codes: 0 };
              return (
                <tr
                  key={lesson.id}
                  className="hover:bg-gray-50 cursor-pointer"
                  onClick={() => setActiveLessonId(lesson.id)}
                >
                  <td className="px-4 py-2.5 text-gray-400 font-mono text-xs">{lesson.lesson_no}</td>
                  <td className="px-4 py-2.5 text-gray-800">
                    {lesson.title}
                    {lesson.summary && (
                      <span className="ml-2 text-xs text-gray-400 truncate max-w-[300px] inline-block align-middle">
                        — {lesson.summary}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    {cnt.slides > 0 ? (
                      <span className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600">{cnt.slides}</span>
                    ) : (
                      <span className="text-xs text-gray-300">—</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    {cnt.codes > 0 ? (
                      <span className="rounded bg-green-50 px-2 py-0.5 text-xs text-green-600">{cnt.codes}</span>
                    ) : (
                      <span className="text-xs text-gray-300">—</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={(e) => { e.stopPropagation(); setActiveLessonId(lesson.id); }}
                      className={`text-xs ${isAdmin ? "text-blue-600 hover:underline" : "text-gray-500 hover:underline"}`}
                    >
                      {isAdmin ? "管理" : "查看"}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 课节详情弹窗 */}
      {activeLesson && (
        <AssetPanel
          lesson={activeLesson}
          isAdmin={isAdmin}
          onClose={() => handleClose(activeLesson.id)}
        />
      )}
    </div>
  );
}
