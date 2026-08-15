from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class NutrientCategory(StrEnum):
    ENERGY = "ENERGY"
    MACRO = "MACRO"
    VITAMIN = "VITAMIN"
    MINERAL = "MINERAL"


class GoalStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class TargetKind(StrEnum):
    TARGET = "TARGET"
    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIMUM"


class UploadPurpose(StrEnum):
    NUTRITION_IMAGE = "NUTRITION_IMAGE"
    DIARY_PDF = "DIARY_PDF"


class UploadStatus(StrEnum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    QUARANTINED = "QUARANTINED"
    DELETED = "DELETED"


class ImageKind(StrEnum):
    AUTO = "AUTO"
    LABEL = "LABEL"
    PLATE = "PLATE"


class ExtractionStatus(StrEnum):
    PROCESSING = "PROCESSING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class MealType(StrEnum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    SNACKS = "SNACKS"


class MealSource(StrEnum):
    MANUAL = "MANUAL"
    IMAGE = "IMAGE"
    PDF = "PDF"
    CHAT = "CHAT"


class NutrientProvenance(StrEnum):
    USER = "USER"
    LABEL_AI = "LABEL_AI"
    PLATE_AI = "PLATE_AI"
    PDF_AI = "PDF_AI"


class PdfImportStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ChatRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"
