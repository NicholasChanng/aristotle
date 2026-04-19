"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "reactflow";

import type { SkillDagNode } from "@/lib/types";

interface SkillNodeData {
  node: SkillDagNode;
}

const STATUS_STYLES: Record<
  SkillDagNode["status"],
  { container: string; dot: string; label: string }
> = {
  locked: {
    container:
      "border-zinc-300 bg-zinc-100 text-zinc-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-400",
    dot: "bg-zinc-400",
    label: "Locked",
  },
  attempted: {
    container:
      "border-sky-400 bg-sky-50 text-sky-900 dark:border-sky-500 dark:bg-sky-950 dark:text-sky-100",
    dot: "bg-sky-500",
    label: "Attempted",
  },
  mastered: {
    container:
      "border-amber-400 bg-amber-50 text-amber-900 dark:border-amber-500 dark:bg-amber-950 dark:text-amber-100",
    dot: "bg-amber-500",
    label: "Mastered",
  },
};

function SkillNodeInner({ data, selected }: NodeProps<SkillNodeData>) {
  const { node } = data;
  const styles = STATUS_STYLES[node.status];
  return (
    <div
      className={[
        "w-[220px] cursor-pointer rounded-lg border-2 px-3 py-2 shadow-sm transition-shadow",
        styles.container,
        selected ? "ring-2 ring-offset-2 ring-primary shadow-md" : "",
      ].join(" ")}
    >
      <Handle type="target" position={Position.Bottom} className="!bg-transparent !border-0" />
      <div className="flex items-start gap-2">
        <span
          aria-hidden
          className={`mt-1 inline-block h-2 w-2 shrink-0 rounded-full ${styles.dot}`}
        />
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold leading-tight">{node.label}</div>
          <div className="mt-0.5 flex items-center gap-2 text-[10px] uppercase tracking-wide opacity-75">
            <span>L{node.level}</span>
            <span>·</span>
            <span>{styles.label}</span>
          </div>
        </div>
      </div>
      <Handle type="source" position={Position.Top} className="!bg-transparent !border-0" />
    </div>
  );
}

export const SkillNode = memo(SkillNodeInner);
