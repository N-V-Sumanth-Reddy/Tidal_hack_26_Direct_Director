'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cn } from '@/lib/utils';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div
      className={cn(
        'prose prose-gray max-w-none',
        'prose-headings:font-bold prose-headings:text-gray-900',
        'prose-h1:text-2xl prose-h1:mb-4',
        'prose-h2:text-xl prose-h2:mb-3 prose-h2:mt-6',
        'prose-h3:text-lg prose-h3:mb-2 prose-h3:mt-4',
        'prose-h4:text-base prose-h4:mb-2 prose-h4:mt-3',
        'prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-4',
        'prose-strong:text-gray-900 prose-strong:font-semibold',
        'prose-em:text-gray-700 prose-em:italic',
        'prose-ul:list-disc prose-ul:pl-6 prose-ul:mb-4',
        'prose-ol:list-decimal prose-ol:pl-6 prose-ol:mb-4',
        'prose-li:text-gray-700 prose-li:mb-1',
        'prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-gray-600',
        'prose-code:bg-gray-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:text-gray-800',
        'prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:p-4 prose-pre:rounded-lg prose-pre:overflow-x-auto',
        'prose-a:text-blue-600 prose-a:underline hover:prose-a:text-blue-700',
        'prose-hr:border-gray-300 prose-hr:my-6',
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
        // Custom rendering for specific elements
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold text-gray-900 mb-4 mt-6 first:mt-0">
            {children}
          </h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-bold text-gray-900 mb-3 mt-6 first:mt-0">
            {children}
          </h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold text-gray-900 mb-2 mt-4 first:mt-0">
            {children}
          </h3>
        ),
        h4: ({ children }) => (
          <h4 className="text-base font-semibold text-gray-900 mb-2 mt-3 first:mt-0">
            {children}
          </h4>
        ),
        p: ({ children }) => (
          <p className="text-gray-700 leading-relaxed mb-4">
            {children}
          </p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-6 mb-4 space-y-1">
            {children}
          </ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-6 mb-4 space-y-1">
            {children}
          </ol>
        ),
        li: ({ children }) => (
          <li className="text-gray-700">
            {children}
          </li>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-4">
            {children}
          </blockquote>
        ),
        code: ({ inline, children, ...props }: any) => {
          if (inline) {
            return (
              <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm text-gray-800 font-mono">
                {children}
              </code>
            );
          }
          return (
            <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto font-mono text-sm" {...props}>
              {children}
            </code>
          );
        },
        strong: ({ children }) => (
          <strong className="font-semibold text-gray-900">
            {children}
          </strong>
        ),
        em: ({ children }) => (
          <em className="italic text-gray-700">
            {children}
          </em>
        ),
        hr: () => (
          <hr className="border-gray-300 my-6" />
        ),
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline hover:text-blue-700"
          >
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
    </div>
  );
}
