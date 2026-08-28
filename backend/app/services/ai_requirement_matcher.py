import json

from app.core.settings import settings
from app.schemas.job_profile import JobRequirement
from app.schemas.requirement_match import RequirementMatchSet
from app.schemas.resume_profile import ResumeProfile
from app.services.ai_client import AIClient

from app.schemas.evidence import Evidence
from app.schemas.evidence_catalog import EvidenceCatalog
from app.services.resume_evidence_catalog import ResumeEvidenceCatalog

class AIRequirementMatcher:
    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client or AIClient()

    def match(
        self,
        requirements: list[JobRequirement],
        resume: ResumeProfile,
    ) -> RequirementMatchSet:
        if not requirements:
            return RequirementMatchSet(
                matches=[]
            )

        evidence_catalog = (
            ResumeEvidenceCatalog().build(
                resume
            )
        )

        client = self.ai_client.get_client()
        schema = RequirementMatchSet.model_json_schema()

        input_data = {
            "requirements": [
                requirement.model_dump(
                    mode="json"
                )
                for requirement in requirements
            ],
            "resume": resume.model_dump(
                mode="json"
            ),
            "allowed_evidences": [
                evidence.model_dump(
                    mode="json"
                )
                for evidence
                in evidence_catalog.evidences
            ],
        }

        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            instructions=(
                "Você é um componente de correspondência semântica "
                "entre requisitos de vaga e evidências de currículo. "

                "Sua única responsabilidade é identificar quais "
                "competências, tecnologias ou evidências do currículo "
                "possuem relação real com cada requisito recebido. "

                "Não atribua notas. "
                "Não calcule aderência. "
                "Não recomende contratação ou reprovação. "
                "Não invente competências ou evidências. "

                "Para cada requisito da vaga, retorne exatamente um "
                "RequirementMatch. "

                "MATCH_TYPE: "

                "EXACT deve ser usado quando o requisito e uma competência "
                "do currículo representam essencialmente o mesmo conceito "
                "de forma explícita. "

                "SEMANTIC deve ser usado quando os nomes forem diferentes, "
                "mas representarem claramente a mesma competência ou "
                "capacidade profissional. "

                "PARTIAL deve ser usado quando o currículo sustentar apenas "
                "parte de um requisito composto ou mais amplo. "

                "NONE deve ser usado quando não existir evidência suficiente "
                "para sustentar qualquer relação real com o requisito. "

                "REQUISITOS COMPOSTOS: "
                "Requisitos como 'Cloud e FinOps', 'DevOps, qualidade e "
                "automação' ou 'gestão de escopo, riscos e prioridades' "
                "podem conter múltiplas capacidades. "
                "Se apenas uma parte estiver sustentada pelo currículo, "
                "classifique como PARTIAL. "

                "EVIDÊNCIAS: "
                "Você receberá uma coleção chamada allowed_evidences. "
                "Somente evidências existentes exatamente nessa coleção "
                "podem ser retornadas em RequirementMatch.evidences. "

                "Não crie, reescreva, resuma, combine ou adapte textos "
                "de evidência. "

                "Quando uma evidência for utilizada, copie integralmente "
                "o objeto correspondente de allowed_evidences, incluindo "
                "text, source, source_reference e page. "

                "Informações existentes no ResumeProfile podem ser usadas "
                "para compreender o contexto semântico, mas somente objetos "
                "presentes em allowed_evidences podem ser retornados como "
                "evidência. "

                "matched_skill_names deve conter somente nomes de skills "
                "presentes no ResumeProfile que sustentem o requisito. "

                "Considere hard_skills, soft_skill_evidences, technologies "
                "e outras informações estruturadas do currículo quando forem "
                "relevantes para compreender a relação. "

                "Não considere similaridade lexical como suficiente. "
                "Exemplo: Java não corresponde a JavaScript. "

                "Não suponha uma competência apenas pelo cargo do candidato. "
                "Toda correspondência deve possuir sustentação documental. "

                "Caso nenhuma correspondência exista, use: "
                "match_type=none, matched_skill_names=[], evidences=[]. "

                "A justification deve explicar de forma objetiva por que "
                "as evidências sustentam totalmente, parcialmente ou não "
                "sustentam o requisito."
            ),
            input=json.dumps(
                input_data,
                ensure_ascii=False,
            ),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "requirement_match_set",
                    "schema": schema,
                    "strict": True,
                }
            },
        )

        if not response.output_text:
            raise ValueError(
                "A IA não retornou correspondências "
                "para os requisitos."
            )

        data = json.loads(
            response.output_text
        )

        result = RequirementMatchSet.model_validate(
            data
        )

        self._validate_match_count(
            requirements,
            result,
        )

        self._validate_evidences(
            evidence_catalog,
            result,
        )

        return result

    @staticmethod
    def _validate_match_count(
        requirements: list[JobRequirement],
        result: RequirementMatchSet,
    ) -> None:
        if len(result.matches) != len(requirements):
            raise ValueError(
                "A IA deve retornar exatamente uma "
                "correspondência por requisito."
            )

        expected_names = {
            requirement.name
            for requirement in requirements
        }

        returned_names = {
            match.requirement_name
            for match in result.matches
        }

        if expected_names != returned_names:
            raise ValueError(
                "Os requisitos retornados pela IA "
                "não correspondem aos requisitos enviados."
            )

    @classmethod
    def _validate_evidences(
        cls,
        evidence_catalog: EvidenceCatalog,
        result: RequirementMatchSet,
    ) -> None:
        def normalize_text(
            value: str,
        ) -> str:
            return " ".join(
                value.strip().casefold().split()
            )

        for match in result.matches:
            validated_evidences: list[Evidence] = []

            for evidence in match.evidences:
                candidates = [
                    catalog_evidence
                    for catalog_evidence
                    in evidence_catalog.evidences
                    if (
                        normalize_text(
                            catalog_evidence.text
                        )
                        == normalize_text(
                            evidence.text
                        )
                        and catalog_evidence.source
                        == evidence.source
                    )
                ]

                if not candidates:
                    raise ValueError(
                        "\n"
                        "A IA retornou uma evidência que não existe "
                        "no catálogo do currículo.\n\n"
                        f"Requisito: {match.requirement_name}\n"
                        f"Match type: {match.match_type}\n\n"
                        "Evidência retornada pela IA:\n"
                        f"  text={evidence.text!r}\n"
                        f"  source={evidence.source!r}\n"
                        "  source_reference="
                        f"{evidence.source_reference!r}\n"
                        f"  page={evidence.page!r}"
                    )

                if len(candidates) > 1:
                    exact_candidates = [
                        candidate
                        for candidate in candidates
                        if (
                            candidate.source_reference
                            == evidence.source_reference
                            and candidate.page
                            == evidence.page
                        )
                    ]

                    if len(exact_candidates) == 1:
                        canonical_evidence = (
                            exact_candidates[0]
                        )
                    else:
                        raise ValueError(
                            "\n"
                            "A evidência retornada pela IA é "
                            "ambígua no catálogo do currículo.\n\n"
                            f"Requisito: "
                            f"{match.requirement_name}\n"
                            f"Texto: {evidence.text!r}\n"
                            f"Source: {evidence.source!r}\n"
                            f"Candidatos encontrados: "
                            f"{len(candidates)}"
                        )

                else:
                    canonical_evidence = candidates[0]

                validated_evidences.append(
                    canonical_evidence
                )

            match.evidences = validated_evidences
            
    @staticmethod
    def _evidence_key(
        evidence: Evidence,
    ) -> tuple:
        return (
            " ".join(
                evidence.text
                .strip()
                .casefold()
                .split()
            ),
            evidence.source.value,
            (
                evidence.source_reference
                .strip()
                .casefold()
                if evidence.source_reference
                else None
            ),
            evidence.page,
        )