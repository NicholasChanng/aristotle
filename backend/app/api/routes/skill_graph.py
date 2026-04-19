"""LLM-powered skill graph routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from openai import APITimeoutError, APIStatusError, LengthFinishReasonError

from ...ai.skills_agent import build_skill_insight, build_skills_graph
from ...models import (
    SkillInsightRequest,
    SkillInsightResponse,
    SkillsGraphRequest,
    SkillsGraphResponse,
)

router = APIRouter(prefix="/skill-graph", tags=["skill-graph"])
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


@router.post("/graph", response_model=SkillsGraphResponse)
async def create_skills_graph(body: SkillsGraphRequest) -> SkillsGraphResponse:
    try:
        graph, metadata = await build_skills_graph(
            course_id=body.course_id,
            lecture_ids=body.lecture_ids,
            mastered_lecture_ids=body.mastered_lecture_ids,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APITimeoutError as exc:
        logger.exception("skill_graph:openai_timeout")
        raise HTTPException(
            status_code=504,
            detail="OpenAI request timed out while building skill graph.",
        ) from exc
    except APIStatusError as exc:
        logger.exception("skill_graph:openai_status_error")
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI API error ({exc.status_code}): {exc.message}",
        ) from exc
    except LengthFinishReasonError as exc:
        logger.exception("skill_graph:length_limit")
        raise HTTPException(
            status_code=502,
            detail="OpenAI response hit token limits while building skill graph.",
        ) from exc

    return SkillsGraphResponse(graph=graph, metadata=metadata)


@router.post("/{skill_id}/insight", response_model=SkillInsightResponse)
async def get_skill_insight(skill_id: str, body: SkillInsightRequest) -> SkillInsightResponse:
    try:
        return await build_skill_insight(
            skill_id=skill_id,
            course_id=body.course_id,
            lecture_ids=body.lecture_ids,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APITimeoutError as exc:
        logger.exception("skill_insight:openai_timeout")
        raise HTTPException(
            status_code=504,
            detail="OpenAI request timed out while generating skill insight.",
        ) from exc
    except APIStatusError as exc:
        logger.exception("skill_insight:openai_status_error")
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI API error ({exc.status_code}): {exc.message}",
        ) from exc
    except LengthFinishReasonError as exc:
        logger.exception("skill_insight:length_limit")
        raise HTTPException(
            status_code=502,
            detail="OpenAI response hit token limits while generating skill insight.",
        ) from exc
