export type UUID = string;
export type IsoDate = string;
export type IsoDateTime = string;
export type UserStatus = "ACTIVE" | "DISABLED" | "DELETED";
export type NutrientCategory = "ENERGY" | "MACRO" | "VITAMIN" | "MINERAL";
export type NutrientUnit = "kcal" | "g" | "mg" | "mcg";
export type NutrientCode = "ENERGY_KCAL" | "PROTEIN" | "CARBOHYDRATE" | "FAT" | "FIBER" | "SUGAR" | "VITAMIN_A" | "VITAMIN_C" | "VITAMIN_D" | "VITAMIN_E" | "VITAMIN_K" | "THIAMIN_B1" | "RIBOFLAVIN_B2" | "NIACIN_B3" | "VITAMIN_B6" | "FOLATE_B9" | "VITAMIN_B12" | "CALCIUM" | "IRON" | "MAGNESIUM" | "PHOSPHORUS" | "POTASSIUM" | "SODIUM" | "ZINC" | "SELENIUM";
export type GoalStatus = "ACTIVE" | "ARCHIVED";
export type TargetKind = "TARGET" | "MINIMUM" | "MAXIMUM";
export type MealType = "BREAKFAST" | "LUNCH" | "DINNER" | "SNACKS";
export type MealSource = "MANUAL" | "IMAGE" | "PDF" | "CHAT";
export type NutrientProvenance = "USER" | "LABEL_AI" | "PLATE_AI" | "PDF_AI";
export type ImageKind = "AUTO" | "LABEL" | "PLATE";
export type ExtractionStatus = "PROCESSING" | "SUCCEEDED" | "FAILED";
export type ReportInterval = "DAY" | "WEEK";
export interface Meta { requestId: string; timezone?: string | null; filters?: Readonly<Record<string, unknown>> | null }
export interface Envelope<T> { data: T; meta: Meta }
export interface Pagination { page: number; limit: number; totalItems: number; totalPages: number; hasNext: boolean; hasPrevious: boolean }
export interface PageEnvelope<T> { data: T[]; pagination: Pagination; meta: Meta }
export interface ApiErrorDetail { field?: string | null | undefined; code: string; message: string }
export interface ApiErrorEnvelope { error: { code: string; message: string; details: ApiErrorDetail[] }; meta: Meta }
