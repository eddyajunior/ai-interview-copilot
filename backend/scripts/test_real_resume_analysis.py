from pathlib import Path

from app.services.ai_resume_analyzer import AIResumeAnalyzer
from app.services.document_parser import DocumentParser


RESUME_PATH = Path(
    "samples/curriculo_teste.pdf"
)


def main():
    parser = DocumentParser()

    document = parser.parse(
        RESUME_PATH
    )

    analyzer = AIResumeAnalyzer()

    resume = analyzer.analyze(
        document
    )

    print(
        resume.model_dump_json(
            indent=2,
            exclude_none=True,
        )
    )


if __name__ == "__main__":
    main()