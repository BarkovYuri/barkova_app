"use client";

import { Eye } from "lucide-react";
import { useEffect, useState } from "react";

import { incrementArticleView } from "../../lib/siteContent";

type Props = {
  slug: string;
  initialCount: number;
};

const SESSION_KEY_PREFIX = "article-viewed:";

/**
 * Серенький счётчик «глаз + число просмотров».
 *
 * При первом заходе на статью в этой сессии — отправляет POST
 * /api/articles/<slug>/view, обновляет цифру локально. Второй раз
 * на ту же статью в той же сессии — счётчик не трогает (защита от
 * накрутки на F5).
 *
 * sessionStorage очищается при закрытии вкладки — то есть человек,
 * вернувшийся завтра, добавит ещё один просмотр, что соответствует
 * реальной метрике «уникальных просмотров за день / визит».
 */
export function ArticleViewCounter({ slug, initialCount }: Props) {
  const [count, setCount] = useState(initialCount);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const key = SESSION_KEY_PREFIX + slug;
    if (window.sessionStorage.getItem(key)) {
      return;
    }
    window.sessionStorage.setItem(key, "1");

    incrementArticleView(slug).then((res) => {
      if (res && typeof res.views_count === "number") {
        setCount(res.views_count);
      }
    });
  }, [slug]);

  return (
    <span
      className="inline-flex items-center gap-1.5 text-sm text-neutral-400"
      aria-label={`${count} просмотров`}
      title="Количество просмотров статьи"
    >
      <Eye className="h-4 w-4" strokeWidth={1.75} />
      <span>{count}</span>
    </span>
  );
}
