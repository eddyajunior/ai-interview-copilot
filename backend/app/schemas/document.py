from enum import Enum

from pydantic import BaseModel


class DocumentType(str, Enum):
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"


class ParsedDocument(BaseModel):
    filename: str
    document_type: DocumentType
    content: str
    character_count: int