import json

from app.core.settings import settings
from app.schemas.document import ParsedDocument
from app.schemas.resume_profile import ResumeProfile
from app.services.ai_client import AIClient


class AIResumeAnalyzer:
    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client or AIClient()

    def analyze(self, document: ParsedDocument) -> ResumeProfile:
        if not document.content.strip():
            raise ValueError(
                "O conteúdo do currículo não pode estar vazio."
            )

        client = self.ai_client.get_client()

        schema = ResumeProfile.model_json_schema()

        document_with_pages = self._build_document_with_pages(
            document
        )

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=(
                "Você é um especialista em análise estruturada de currículos. "

                "Extraia somente informações explicitamente presentes no currículo. "
                "Não invente experiências, competências, tecnologias, datas, "
                "certificações, responsabilidades ou resultados. "

                "O currículo será fornecido com marcadores no formato "
                "'--- PAGE N ---'. Esses marcadores representam a página original "
                "do documento. "

                "EXPERIÊNCIAS: "
                "Extraia empresa, cargo, período, responsabilidades, realizações "
                "e tecnologias explicitamente associadas à experiência. "

                "HARD SKILLS: "
                "Representam conhecimentos, capacidades técnicas, práticas, "
                "disciplinas ou conhecimentos profissionais. "
                "Exemplos incluem arquitetura de software, sistemas distribuídos, "
                "FinOps, APIs, segurança, práticas de engenharia e conhecimentos "
                "de domínio técnico. "

                "SOFT SKILLS: "
                "Representam competências comportamentais ou interpessoais. "
                "Somente registre uma soft skill quando existir evidência explícita "
                "que sustente essa conclusão. "
                "Não deduza soft skills apenas pelo cargo do candidato. "
                "Não transforme responsabilidades profissionais em soft skills. "

                "TECHNOLOGIES: "
                "Registre somente linguagens de programação, frameworks, "
                "bibliotecas, bancos de dados, ferramentas, plataformas, "
                "serviços ou produtos tecnológicos explicitamente mencionados. "
                "Não classifique como tecnologia conceitos, práticas, disciplinas, "
                "metodologias, competências, domínios de negócio ou regulações. "
                "Por exemplo, arquitetura distribuída, FinOps, PIX, APIs, "
                "compliance e Bacen MED não devem ser classificados como tecnologias. "

                "EVIDÊNCIAS: "
                "Toda hard skill, soft skill ou tecnologia registrada deve possuir "
                "ao menos uma evidência concreta encontrada no currículo. "
                "O campo text deve conter o trecho que sustenta a evidência. "
                "O campo source deve indicar corretamente a origem da informação. "
                "O campo source_reference deve identificar a experiência, formação, "
                "certificação ou seção quando isso for possível. "
                "O campo page deve receber o número do marcador PAGE em que a "
                "evidência foi encontrada. "
                "Somente use null em page quando realmente não for possível "
                "determinar a página. "

                "RESULTADOS MENSURÁVEIS: "
                "measurable_results deve conter somente resultados que possuam "
                "uma medida objetiva explícita no currículo, como percentual, "
                "valor financeiro, quantidade, volume, prazo, redução de tempo, "
                "aumento mensurado ou outra métrica objetiva. "
                "Não registre como measurable_result afirmações puramente "
                "qualitativas como aumento de qualidade, melhoria de eficiência "
                "ou ganho de performance quando nenhuma medida objetiva estiver "
                "explicitamente associada. "

                "LIDERANÇA: "
                "leadership_evidences deve conter somente evidências explícitas "
                "de liderança técnica, liderança de pessoas, gestão de times, "
                "mentoria, desenvolvimento de pessoas ou responsabilidade "
                "organizacional relacionada à liderança. "

                "Quando uma informação não estiver disponível, use null nos "
                "campos que aceitam null e listas vazias nos campos de coleção. "

                "Não atribua nota, aderência, senioridade inferida ou avaliação "
                "ao candidato. "
                "Não compare o candidato com nenhuma vaga. "

                "O objetivo desta análise é criar uma representação factual, "
                "estruturada e rastreável do currículo."
            ),
            input=document_with_pages,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "resume_profile",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

        if not response.output_text:
            raise ValueError(
                "A IA não retornou conteúdo para o currículo."
            )

        data = json.loads(response.output_text)

        return ResumeProfile.model_validate(data)

    def _build_document_with_pages(
        self,
        document: ParsedDocument,
    ) -> str:
        if not document.pages:
            return document.content

        page_contents = []

        for page in document.pages:
            page_contents.append(
                f"--- PAGE {page.number} ---\n"
                f"{page.content.strip()}"
            )

        return "\n\n".join(page_contents)