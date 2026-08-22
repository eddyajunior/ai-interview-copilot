from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"
    RAW_TEXT = "raw_text"


class DocumentPage(BaseModel):
    number: int = Field(ge=1)
    content: str


class ParsedDocument(BaseModel):
    filename: str
    document_type: DocumentType

    content: str
    character_count: int

    page_count: int = Field(ge=1)
    pages: List[DocumentPage] = Field(default_factory=list)