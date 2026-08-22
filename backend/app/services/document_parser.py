from pathlib import Path

from app.schemas.document import DocumentType, ParsedDocument


class UnsupportedDocumentTypeError(Exception):
    pass


class DocumentParser:
    SUPPORTED_TYPES = {
        ".txt": DocumentType.TXT,
        ".pdf": DocumentType.PDF,
        ".docx": DocumentType.DOCX,
    }

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_TYPES:
            raise UnsupportedDocumentTypeError(
                f"Formato não suportado: {extension}"
            )

        document_type = self.SUPPORTED_TYPES[extension]

        if document_type == DocumentType.TXT:
            content = self._parse_txt(path)
        else:
            raise NotImplementedError(
                f"Parser para {document_type.value} ainda não implementado."
            )

        content = self._normalize_text(content)

        return ParsedDocument(
            filename=path.name,
            document_type=document_type,
            content=content,
            character_count=len(content),
        )

    def _parse_txt(self, path: Path) -> str:
        return path.read_text(
            encoding="utf-8"
        )

    def _normalize_text(self, text: str) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)