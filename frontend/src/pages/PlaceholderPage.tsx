interface Props {
  title: string;
  description?: string;
}

export default function PlaceholderPage({ title, description }: Props) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-2 text-gray-400">
      <span className="text-4xl">🚧</span>
      <p className="text-base font-medium text-gray-500">{title}</p>
      <p className="text-sm">{description ?? "功能开发中，敬请期待"}</p>
    </div>
  );
}
