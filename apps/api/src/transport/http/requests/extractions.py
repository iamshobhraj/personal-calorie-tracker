from src.persistence.models.enums import ImageKind
from src.transport.http.requests.common import StrictRequestModel


class ExtractionCreateRequest(StrictRequestModel):
    image_kind: ImageKind = ImageKind.AUTO
