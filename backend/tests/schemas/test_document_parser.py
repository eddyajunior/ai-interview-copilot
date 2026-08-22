import pytest

from app.schemas.document import DocumentType
from app.services.document_parser import (
    DocumentParser,
    UnsupportedDocumentTypeError,
)


def test_parse_txt_document(tmp_path):
    file = tmp_path / "curriculo.txt"

    file.write_text(
        """
        João Silva

        Senior Software Engineer

        Java
        AWS
        Kafka
        """,
        encoding="utf-8",
    )

    parser = DocumentParser()

    document = parser.parse(file)

    assert document.filename == "curriculo.txt"
    assert document.document_type == DocumentType.TXT

    assert document.content == (
        "João Silva\n"
        "Senior Software Engineer\n"
        "Java\n"
        "AWS\n"
        "Kafka"
    )

    assert document.character_count > 0


def test_document_not_found():
    parser = DocumentParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("arquivo_inexistente.txt")


def test_unsupported_document_type(tmp_path):
    file = tmp_path / "curriculo.xyz"
    file.write_text("teste", encoding="utf-8")

    parser = DocumentParser()

    with pytest.raises(UnsupportedDocumentTypeError):
        parser.parse(file)