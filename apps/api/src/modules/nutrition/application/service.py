from src.persistence.repositories.nutrients import NutrientRepository


class NutritionService:
    def __init__(self, repository: NutrientRepository) -> None:
        self._repository = repository
