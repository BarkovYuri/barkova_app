import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Безопасный рендер Markdown-тела статьи.
 *
 * react-markdown по умолчанию НЕ рендерит raw HTML — пользовательский
 * Markdown из админки безопасен для вставки. Дополнительно применяем
 * remark-gfm (таблицы, чек-листы, autolink, strikethrough).
 *
 * Стилизация — Tailwind через классы на наших узлах. (Можно было бы
 * @tailwindcss/typography, но добавлять отдельный плагин ради одной
 * страницы избыточно — ручная настройка контролируемая и без deps.)
 */
export function ArticleBody({ markdown }: { markdown: string }) {
  return (
    <div className="article-body text-base sm:text-lg leading-relaxed text-neutral-800">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h2: ({ children }) => (
            <h2 className="mt-12 mb-4 text-2xl sm:text-3xl font-bold text-neutral-900 tracking-tight">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mt-8 mb-3 text-xl sm:text-2xl font-semibold text-neutral-900">
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className="my-5 text-neutral-700 leading-relaxed">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="my-5 space-y-2 list-disc list-outside pl-6 text-neutral-700">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-5 space-y-2 list-decimal list-outside pl-6 text-neutral-700">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          a: ({ href, children }) => (
            <a
              href={href}
              target={href?.startsWith("http") ? "_blank" : undefined}
              rel={href?.startsWith("http") ? "noreferrer" : undefined}
              className="text-primary-700 underline-offset-4 underline decoration-primary-300 hover:decoration-primary-700"
            >
              {children}
            </a>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-neutral-900">{children}</strong>
          ),
          em: ({ children }) => <em className="italic">{children}</em>,
          blockquote: ({ children }) => (
            <blockquote className="my-6 border-l-4 border-primary-400 bg-primary-50 px-5 py-3 italic text-neutral-700 rounded-r-lg">
              {children}
            </blockquote>
          ),
          code: ({ children }) => (
            <code className="rounded bg-neutral-100 px-1.5 py-0.5 text-[0.92em] font-mono text-neutral-800">
              {children}
            </code>
          ),
          hr: () => <hr className="my-10 border-neutral-200" />,
          table: ({ children }) => (
            <div className="my-6 overflow-x-auto">
              <table className="w-full border-collapse text-sm">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border-b-2 border-neutral-300 px-3 py-2 text-left font-semibold text-neutral-900">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-b border-neutral-200 px-3 py-2 text-neutral-700">
              {children}
            </td>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
