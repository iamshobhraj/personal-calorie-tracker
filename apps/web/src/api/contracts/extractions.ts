import type { ExtractionStatus, MealType, NutrientCode, NutrientUnit, UUID } from "./common";
import type { Quantity } from "./meals";
export interface ExtractionNutrient { code: NutrientCode; amount: number; unit: NutrientUnit; confidence: number; provenance: "LABEL_AI" | "PLATE_AI" }
export interface ExtractionResult { imageKind: "LABEL" | "PLATE"; foodName: string; quantity: Quantity; suggestedMealType: MealType | null; nutrients: ExtractionNutrient[]; overallConfidence: number; warnings: string[]; requiresUserConfirmation: true }
export interface NutritionExtraction { id: UUID; status: ExtractionStatus; result: ExtractionResult | null; failure: { code: string; message: string } | null }
