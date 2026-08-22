import json

from app.core.settings import settings
from app.schemas.document import ParsedDocument
from app.schemas.job_profile import JobProfile
from app.services.ai_client import AIClient


class AIJobAnalyzer:
    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client or AIClient()

    def analyze(self, document: ParsedDocument) -> JobProfile:
        if not document.content.strip():
            raise ValueError("O conteúdo da vaga não pode estar vazio.")

        client = self.ai_client.get_client()

        schema = JobProfile.model_json_schema()

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=(
                "Você é um especialista em análise estruturada de vagas profissionais. "

                "Analise exclusivamente as informações presentes na descrição fornecida. "
                "Não invente requisitos, tecnologias, competências ou responsabilidades. "

                "Classifique os elementos da vaga seguindo estas regras: "

                "hard_skills representam conhecimentos, capacidades técnicas, práticas "
                "de engenharia, arquitetura, processos ou conhecimentos profissionais; "

                "soft_skills representam comportamentos e competências interpessoais, "
                "como comunicação, autonomia, colaboração, resolução de problemas, "
                "liderança e trabalho em equipe; "

                "technologies representam linguagens, frameworks, plataformas, bancos "
                "de dados, ferramentas e produtos tecnológicos; "

                "responsibilities representam atividades que o profissional deverá executar; "

                "differentiators representam explicitamente requisitos descritos como "
                "diferenciais, desejáveis ou não obrigatórios. "

                "Não transforme responsabilidades em soft skills. "
                "Não duplique uma mesma competência desnecessariamente entre categorias. "

                "Quando liderança técnica for apresentada como competência comportamental "
                "ou capacidade de influência, classifique-a como soft skill. "

                "Use importance='required' para requisitos obrigatórios, "
                "'desired' para diferenciais ou desejáveis e "
                "'optional' somente quando explicitamente opcional. "

                "Normalize a senioridade utilizando preferencialmente: "
                "junior, mid, senior, specialist ou lead. "

                "Retorne exclusivamente informações suportadas pela descrição da vaga."
            ),
            input=document.content,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "job_profile",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

        if not response.output_text:
            raise ValueError("A IA não retornou conteúdo para a vaga.")

        data = json.loads(response.output_text)

        return JobProfile.model_validate(data)
    