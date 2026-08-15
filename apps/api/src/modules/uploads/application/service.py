from src.persistence.repositories.uploads import UploadRepository


class UploadService:
    def __init__(self, repository: UploadRepository) -> None:
        self._repository = repository
