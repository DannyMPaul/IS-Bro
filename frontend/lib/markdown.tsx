import React from "react";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className = "",
}) => {
  const renderMarkdown = (text: string) => {
    // Convert markdown to JSX elements
    let html = text;

    // Code blocks (```code```)
    html = html.replace(
      /```([^`]+)```/g,
      '<pre class="bg-gray-800 text-green-400 p-3 rounded-lg my-2 overflow-x-auto"><code>$1</code></pre>'
    );

    // Inline code (`code`)
    html = html.replace(
      /`([^`]+)`/g,
      '<code class="bg-gray-200 dark:bg-slate-800 text-blue-800 dark:text-yellow-300 px-1 py-0.5 rounded text-sm">$1</code>'
    );

    // Bold (**text** or __text__)
    html = html.replace(
      /\*\*([^*]+)\*\*/g,
      '<strong class="font-bold">$1</strong>'
    );
    html = html.replace(
      /__([^_]+)__/g,
      '<strong class="font-bold">$1</strong>'
    );

    // Italic (*text* or _text_)
    html = html.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em class="italic">$1</em>');

    // Links [text](url)
    html = html.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-yellow-400 underline hover:text-blue-800 dark:hover:text-yellow-200">$1</a>'
    );

    // Line breaks
    html = html.replace(/\n/g, "<br />");

    // Lists (- item or * item)
    const lines = html.split("<br />");
    let inList = false;
    const processedLines = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.match(/^[-*]\s+/)) {
        if (!inList) {
          processedLines.push(
            '<ul class="list-disc list-inside my-2 space-y-1">'
          );
          inList = true;
        }
        const listItem = line.replace(/^[-*]\s+/, "");
        processedLines.push(`<li class="ml-4">${listItem}</li>`);
      } else {
        if (inList) {
          processedLines.push("</ul>");
          inList = false;
        }
        if (line) {
          processedLines.push(line);
        }
      }
    }

    if (inList) {
      processedLines.push("</ul>");
    }

    return processedLines.join("<br />");
  };

  return (
    <div
      className={`markdown-content ${className}`}
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  );
};

// Simple syntax highlighter for code blocks
export const SyntaxHighlighter: React.FC<{
  code: string;
  language?: string;
}> = ({ code, language = "text" }) => {
  return (
    <pre className="bg-gray-900 dark:bg-slate-950 text-green-400 p-4 rounded-lg my-2 overflow-x-auto border border-gray-700">
      <code className="text-sm font-mono">{code}</code>
    </pre>
  );
};
