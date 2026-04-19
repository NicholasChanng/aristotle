"""PyPDFLoader-based ingestion for ad-hoc PDFs.

Mirrors the canonical LangChain PDF RAG pattern:
    PyPDFLoader → RecursiveCharacterTextSplitter → OpenAIEmbeddings → Chroma

Use this path for courses or supplementary material that do NOT ship with
pre-chunked JSONs. For the cs188 demo course keep using the token-based
chunks from cs188/chunk_slides.py (preserved in cs188/lectures/*.json) —
those have richer metadata than PyPDFLoader emits by default.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document as LCDocument
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings
from ..enums import DocType
from ..models import CourseDocument
from .chroma import upsert_documents
from .documents import build_context_header


def load_pdf_pages(pdf_path: Path) -> list[LCDocument]:
    """One LCDocument per PDF page, with `metadata.page` starting at 0."""
    return PyPDFLoader(str(pdf_path)).load()


def split_pages(
    pages: list[LCDocument],
    *,
    chunk_size_chars: int = 2000,
    chunk_overlap_chars: int = 200,
) -> list[LCDocument]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_chars,
        chunk_overlap=chunk_overlap_chars,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(pages)


def pdf_chunks_to_course_docs(
    chunks: list[LCDocument],
    *,
    course_id: str,
    course_name: str,
    lecture_id: str,
    lecture_order: int,
    lecture_title: str,
) -> list[CourseDocument]:
    header = build_context_header(course_name, lecture_order, lecture_title)
    course_slug = course_id.replace("-", "_")

    docs: list[CourseDocument] = []
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        chunk_type = "intro" if i == 0 else "summary" if i == total - 1 else "body"
        page_zero_indexed = chunk.metadata.get("page", 0)
        docs.append(
            CourseDocument(
                doc_id=f"{course_slug}_{lecture_id}_pdfchunk_{i:03d}",
                course_id=course_id,
                doc_type=DocType.LECTURE_SLIDE_CHUNK,
                text=f"{header} {chunk.page_content}",
                metadata={
                    "lecture_id": lecture_id,
                    "chunk_index": i,
                    "source_page": int(page_zero_indexed) + 1,
                    "chunk_type": chunk_type,
                },
            )
        )
    return docs


async def ingest_pdf(
    pdf_path: Path,
    *,
    course_id: str,
    course_name: str,
    lecture_id: str,
    lecture_order: int,
    lecture_title: str,
) -> int:
    """End-to-end: load PDF → split → embed → upsert to Chroma. Returns doc count."""
    pages = load_pdf_pages(pdf_path)
    chunks = split_pages(pages)
    docs = pdf_chunks_to_course_docs(
        chunks,
        course_id=course_id,
        course_name=course_name,
        lecture_id=lecture_id,
        lecture_order=lecture_order,
        lecture_title=lecture_title,
    )

    embedder = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
    embeddings = await embedder.aembed_documents([d.text for d in docs])
    upsert_documents(docs, embeddings)
    return len(docs)
