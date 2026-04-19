"use client";

import { create } from "zustand";

import { api } from "@/lib/api";
import type {
  SkillDagGraph,
  SkillInsightResponse,
  SkillsGraphMetadata,
} from "@/lib/types";

type InsightEntry =
  | { status: "loading" }
  | { status: "ready"; data: SkillInsightResponse }
  | { status: "error"; message: string };

interface SkillGraphState {
  courseId: string | null;
  signature: string | null;
  graph: SkillDagGraph | null;
  metadata: SkillsGraphMetadata | null;
  status: "idle" | "loading" | "ready" | "error";
  error: string | null;
  insights: Record<string, InsightEntry>;

  loadGraph: (args: {
    courseId: string;
    lectureIds: string[];
    masteredLectureIds: string[];
  }) => Promise<void>;
  loadInsight: (args: {
    skillId: string;
    courseId: string;
    lectureIds: string[];
  }) => Promise<void>;
  reset: () => void;
}

function signatureFor(courseId: string, mastered: string[]): string {
  const sorted = [...mastered].sort();
  return `${courseId}::${sorted.join(",")}`;
}

export const useSkillGraphStore = create<SkillGraphState>((set, get) => ({
  courseId: null,
  signature: null,
  graph: null,
  metadata: null,
  status: "idle",
  error: null,
  insights: {},

  loadGraph: async ({ courseId, lectureIds, masteredLectureIds }) => {
    const sig = signatureFor(courseId, masteredLectureIds);
    const state = get();
    if (state.signature === sig && state.status === "ready") return;
    set({
      courseId,
      signature: sig,
      status: "loading",
      error: null,
      insights: {},
    });
    try {
      const resp = await api.skillGraph.build({
        course_id: courseId,
        lecture_ids: lectureIds,
        mastered_lecture_ids: masteredLectureIds,
      });
      if (get().signature !== sig) return;
      set({
        graph: resp.graph,
        metadata: resp.metadata,
        status: "ready",
        error: null,
      });
    } catch (err) {
      if (get().signature !== sig) return;
      set({
        status: "error",
        error: err instanceof Error ? err.message : String(err),
      });
    }
  },

  loadInsight: async ({ skillId, courseId, lectureIds }) => {
    const existing = get().insights[skillId];
    if (existing && existing.status !== "error") return;
    set((s) => ({
      insights: { ...s.insights, [skillId]: { status: "loading" } },
    }));
    try {
      const data = await api.skillGraph.insight(skillId, {
        course_id: courseId,
        lecture_ids: lectureIds,
        graph: get().graph,
      });
      set((s) => ({
        insights: { ...s.insights, [skillId]: { status: "ready", data } },
      }));
    } catch (err) {
      set((s) => ({
        insights: {
          ...s.insights,
          [skillId]: {
            status: "error",
            message: err instanceof Error ? err.message : String(err),
          },
        },
      }));
    }
  },

  reset: () =>
    set({
      courseId: null,
      signature: null,
      graph: null,
      metadata: null,
      status: "idle",
      error: null,
      insights: {},
    }),
}));
