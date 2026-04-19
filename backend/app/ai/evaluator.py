"""Claude-based rubric evaluator for free-form answers (SRS 9.3).

ChatPromptTemplate | ChatAnthropic.with_structured_output(_Evaluation)
Returns (correct, partial_credit, feedback).
"""

from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ..config import settings
from ..models import Question


class _Evaluation(BaseModel):
    correct: bool = Field(description="True iff the answer is substantively correct")
    partial_credit: float = Field(
        ge=0.0, le=1.0, description="Credit 0.0-1.0; 1.0 only if fully correct"
    )
    feedback: str = Field(description="One sentence in the monster's voice")


_SYSTEM_PROMPT = (
    "You are an impartial grader. Use the rubric strictly. Be generous on "
    "phrasing and formatting, but strict on technical correctness. Never let "
    "a confidently-stated wrong answer earn full credit."
)

_USER_PROMPT = """Question: {prompt}
Expected answer: {correct_answer}
Rubric: {rubric}

Student's answer:
{user_answer}

Grade the student. Speak the feedback in {monster_name}'s voice (one sentence).
If the student's answer is partially correct, award partial_credit between 0 and 1.
"""


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-5-mini",
        api_key=settings.openai_api_key,
        max_tokens=512,
        timeout=settings.generation_timeout_s,
    )


async def evaluate_answer(
    question: Question,
    user_answer: str,
    monster_name: str = "the Oracle",
) -> tuple[bool, float, str]:
    prompt = ChatPromptTemplate.from_messages(
        [("system", _SYSTEM_PROMPT), ("human", _USER_PROMPT)]
    )
    chain = prompt | _get_llm().with_structured_output(_Evaluation)

    result: _Evaluation = await chain.ainvoke(
        {
            "prompt": question.prompt,
            "correct_answer": question.correct_answer,
            "rubric": question.rubric or "Standard correctness grading.",
            "user_answer": user_answer,
            "monster_name": monster_name,
        }
    )
    return result.correct, result.partial_credit, result.feedback
