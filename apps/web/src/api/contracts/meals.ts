import type { IsoDate, IsoDateTime, MealSource, MealType, NutrientCode, NutrientProvenance, UUID } from "./common";
import type { NutrientAmount } from "./nutrition";
export interface Quantity { value: number; unit: string; description: string | null }
export interface MealEntry { id: UUID; mealType: MealType; foodName: string; quantity: Quantity; occurredAt: IsoDateTime; timezone: string; localDate: IsoDate; source: MealSource; sourceExtractionId: UUID | null; notes: string | null; nutrients: NutrientAmount[]; createdAt: IsoDateTime; updatedAt: IsoDateTime }
export interface MealNutrientInput { code: NutrientCode; amount: number; confidence?: number | null; provenance?: NutrientProvenance }
export interface MealUpsertInput { mealType: MealType; foodName: string; quantity: { value: number; unit: string; description?: string | null }; occurredAt: IsoDateTime; timezone: string; source: MealSource; sourceExtractionId: UUID | null; notes: string | null; nutrients: MealNutrientInput[] }
