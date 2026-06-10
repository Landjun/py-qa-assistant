import client from "./client";

export interface Course {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  lesson_count: number;
}

export interface Lesson {
  id: number;
  course_id: number;
  lesson_no: number;
  title: string;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface LessonAsset {
  id: number;
  lesson_id: number;
  asset_type: "slide" | "code" | "other";
  filename: string;
  file_path: string;
  file_type: string;
  size_bytes: number;
  created_at: string;
}

// ─── 课程 ────────────────────────────────────────────────────────────────────

export async function listCourses(): Promise<Course[]> {
  const res = await client.get<Course[]>("/courses");
  return res.data;
}

export async function createCourse(name: string, description = ""): Promise<Course> {
  const res = await client.post<Course>("/courses", { name, description });
  return res.data;
}

export async function init48(): Promise<Course> {
  const res = await client.post<Course>("/courses/init-48");
  return res.data;
}

// ─── 课节 ────────────────────────────────────────────────────────────────────

export async function listLessons(courseId: number): Promise<Lesson[]> {
  const res = await client.get<Lesson[]>(`/courses/${courseId}/lessons`);
  return res.data;
}

export async function getLesson(lessonId: number): Promise<Lesson> {
  const res = await client.get<Lesson>(`/lessons/${lessonId}`);
  return res.data;
}

export async function updateLesson(
  lessonId: number,
  data: { title?: string; summary?: string | null },
): Promise<Lesson> {
  const res = await client.patch<Lesson>(`/lessons/${lessonId}`, data);
  return res.data;
}

// ─── 课节资源 ─────────────────────────────────────────────────────────────────

export async function listAssets(lessonId: number): Promise<LessonAsset[]> {
  const res = await client.get<LessonAsset[]>(`/lessons/${lessonId}/assets`);
  return res.data;
}

export async function uploadAsset(
  lessonId: number,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<LessonAsset> {
  const form = new FormData();
  form.append("file", file);
  const res = await client.post<LessonAsset>(`/lessons/${lessonId}/assets`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: onProgress
      ? (e) => onProgress(Math.round(((e.loaded ?? 0) / (e.total ?? 1)) * 100))
      : undefined,
  });
  return res.data;
}

export async function deleteAsset(assetId: number): Promise<void> {
  await client.delete(`/assets/${assetId}`);
}

export function assetUrl(asset: LessonAsset): string {
  return `/static/${asset.file_path}`;
}

export function fmtBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
