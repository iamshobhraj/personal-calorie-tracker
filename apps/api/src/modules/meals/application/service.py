from uuid import UUID

from src.persistence.models.enums import ExtractionStatus, MealSource, NutrientProvenance
from src.persistence.models.meal import MealEntry, MealEntryNutrient
from src.persistence.repositories.extractions import ExtractionRepository
from src.persistence.repositories.meals import MealRepository
from src.persistence.repositories.nutrients import NutrientRepository
from src.shared.errors.api_error import ApiError
from src.shared.time.timezone import local_date
from src.transport.http.requests.meals import MealUpsertRequest


class MealService:
    def __init__(
        self,
        meals: MealRepository,
        nutrients: NutrientRepository,
        extractions: ExtractionRepository,
    ) -> None:
        self._meals, self._nutrients, self._extractions = meals, nutrients, extractions

    async def _model(self, user_id: UUID, request: MealUpsertRequest) -> MealEntry:
        definitions = await self._nutrients.get_mapping_by_codes(
            row.code for row in request.nutrients
        )
        if len(definitions) != len(request.nutrients):
            raise ApiError(422, "UNKNOWN_NUTRIENT", "One or more nutrient codes are invalid.")
        extraction = None
        if request.source is MealSource.IMAGE:
            extraction = await self._extractions.get_owned(user_id, request.source_extraction_id)  # type: ignore[arg-type]
            if (
                extraction is None
                or extraction.status is not ExtractionStatus.SUCCEEDED
                or await self._meals.owns_extraction(user_id, extraction.id)
            ):
                raise ApiError(
                    422, "INVALID_EXTRACTION", "The image extraction cannot be used for this meal."
                )
        meal = MealEntry(
            user_id=user_id,
            meal_type=request.meal_type,
            food_name=request.food_name,
            quantity=request.quantity.value,
            quantity_unit=request.quantity.unit,
            portion_description=request.quantity.description,
            occurred_at=request.occurred_at,
            entry_timezone=request.timezone,
            local_date=local_date(request.occurred_at, request.timezone),
            source=request.source,
            source_extraction_id=request.source_extraction_id,
            notes=request.notes,
        )
        provenance = (
            NutrientProvenance.LABEL_AI
            if extraction is not None and extraction.image_kind.value == "LABEL"
            else NutrientProvenance.PLATE_AI
            if extraction is not None
            else NutrientProvenance.USER
        )
        meal.nutrients = [
            MealEntryNutrient(
                user_id=user_id,
                nutrient_id=definitions[row.code].id,
                amount=row.amount,
                confidence=row.confidence if extraction is not None else None,
                provenance=provenance,
                nutrient=definitions[row.code],
            )
            for row in request.nutrients
        ]
        return meal

    async def create(self, user_id: UUID, request: MealUpsertRequest) -> MealEntry:
        meal = await self._model(user_id, request)
        self._meals.add(meal)
        return meal

    async def replace(self, user_id: UUID, meal_id: UUID, request: MealUpsertRequest) -> MealEntry:
        replacement = await self._model(user_id, request)
        meal = await self._meals.replace_owned(user_id, meal_id, replacement)
        if meal is None:
            raise ApiError(404, "NOT_FOUND", "The requested resource was not found.")
        return meal
