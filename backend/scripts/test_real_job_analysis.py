from app.services.ai_job_analyzer import AIJobAnalyzer
from app.services.document_parser import DocumentParser


JOB_DESCRIPTION = """
Senior Software Engineer

Buscamos profissional com experiência sólida em desenvolvimento
de sistemas distribuídos e arquitetura de microsserviços.

Requisitos:
- Java e Spring Boot
- AWS
- Kafka
- Docker
- Kubernetes
- PostgreSQL
- Experiência com arquitetura de software

Esperamos também boa comunicação, autonomia, resolução de problemas
e capacidade de trabalhar em equipe.

Experiência com liderança técnica será considerada um diferencial.

Responsabilidades:
- Desenvolver aplicações escaláveis
- Participar das decisões arquiteturais
- Apoiar tecnicamente outros desenvolvedores
- Contribuir com boas práticas de engenharia
"""


def main():
    parser = DocumentParser()

    document = parser.parse_text(
        JOB_DESCRIPTION,
        source_name="vaga_teste_real",
    )

    analyzer = AIJobAnalyzer()

    job = analyzer.analyze(document)

    print(
        job.model_dump_json(
            indent=2,
            exclude_none=True,
        )
    )


if __name__ == "__main__":
    main()