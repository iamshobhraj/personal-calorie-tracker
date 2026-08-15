from decimal import Decimal

from src.persistence.models.enums import ImageKind
from src.persistence.repositories.nutrients import NutrientRepository
from src.services.ai.output_schema import AiNutritionResult
from src.shared.errors.api_error import ApiError


class NutritionImageService:
    def __init__(self, nutrients: NutrientRepository) -> None:
        self._nutrients = nutrients

    async def validate(
        self, result: AiNutritionResult, requested_kind: ImageKind
    ) -> AiNutritionResult:
        if requested_kind is not ImageKind.AUTO and result.image_kind != requested_kind.value:
            raise ApiError(
                422, "INVALID_AI_OUTPUT", "The image result did not match the requested image kind."
            )
        codes = [nutrient.code for nutrient in result.nutrients]
        definitions = await self._nutrients.get_mapping_by_codes(codes)
        if len(definitions) != len(codes) or len(set(codes)) != len(codes):
            raise ApiError(
                422, "INVALID_AI_OUTPUT", "The image result contained unsupported nutrients."
            )
        for nutrient in result.nutrients:
            if definitions[
                nutrient.code
            ].canonical_unit != nutrient.unit or nutrient.amount > Decimal("100000"):
                raise ApiError(
                    422, "INVALID_AI_OUTPUT", "The image result contained invalid nutrient values."
                )
        return result
