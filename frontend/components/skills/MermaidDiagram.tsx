"use client";

import { useEffect, useRef, useState } from "react";

interface MermaidDiagramProps {
  code: string;
}

let mermaidInitialized = false;
let renderCounter = 0;

export function MermaidDiagram({ code }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      const mermaid = (await import("mermaid")).default;
      if (!mermaidInitialized) {
        mermaid.initialize({
          startOnLoad: false,
          theme: "neutral",
          securityLevel: "strict",
          fontFamily: "inherit",
        });
        mermaidInitialized = true;
      }
      const id = `mermaid-${++renderCounter}`;
      try {
        const { svg } = await mermaid.render(id, code);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      }
    }

    render();
    return () => {
      cancelled = true;
    };
  }, [code]);

  if (error) {
    return (
      <div className="rounded border border-destructive/40 bg-destructive/10 p-3 text-xs text-destructive">
        Failed to render diagram: {error}
        <pre className="mt-2 overflow-auto whitespace-pre-wrap text-[11px] opacity-80">
          {code}
        </pre>
      </div>
    );
  }

  return <div ref={containerRef} className="flex justify-center [&_svg]:max-w-full" />;
}
