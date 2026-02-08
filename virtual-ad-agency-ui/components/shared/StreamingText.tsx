'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import type { StreamingTextProps } from '@/lib/types';

// ============================================================================
// Component
// ============================================================================

export function StreamingText({ text, isComplete }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);

  // Animate text streaming
  useEffect(() => {
    if (isComplete) {
      setDisplayedText(text);
      return;
    }

    // Gradually reveal text
    if (displayedText.length < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(text.slice(0, displayedText.length + 1));
      }, 20); // 20ms per character for smooth animation

      return () => clearTimeout(timeout);
    }
  }, [text, displayedText, isComplete]);

  // Cursor blink animation
  useEffect(() => {
    if (isComplete) {
      setCursorVisible(false);
      return;
    }

    const interval = setInterval(() => {
      setCursorVisible((v) => !v);
    }, 500);

    return () => clearInterval(interval);
  }, [isComplete]);

  return (
    <div className="relative">
      <p className="whitespace-pre-wrap">
        {displayedText}
        {!isComplete && (
          <span
            className={cn(
              'inline-block w-0.5 h-5 bg-blue-600 ml-0.5 align-middle',
              cursorVisible ? 'opacity-100' : 'opacity-0',
              'transition-opacity duration-100'
            )}
          />
        )}
      </p>
    </div>
  );
}

// ============================================================================
// Variants
// ============================================================================

export function StreamingTextBlock({
  text,
  isComplete,
  title,
}: StreamingTextProps & { title?: string }) {
  return (
    <div className="rounded-lg border bg-white p-6">
      {title && (
        <h3 className="text-lg font-semibold mb-4 text-gray-900">{title}</h3>
      )}
      <div className="prose prose-sm max-w-none">
        <StreamingText text={text} isComplete={isComplete} />
      </div>
      {!isComplete && (
        <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
          <div className="flex gap-1">
            <div className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-pulse" />
            <div className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-pulse [animation-delay:0.2s]" />
            <div className="h-1.5 w-1.5 rounded-full bg-blue-600 animate-pulse [animation-delay:0.4s]" />
          </div>
          <span>Generating...</span>
        </div>
      )}
    </div>
  );
}
