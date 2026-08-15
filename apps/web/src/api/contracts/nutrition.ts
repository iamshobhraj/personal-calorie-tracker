import type { NutrientCategory, NutrientCode, NutrientProvenance, NutrientUnit } from "./common";
export interface NutrientCatalogItem { code: NutrientCode; name: string; category: NutrientCategory; unit: NutrientUnit; displayOrder: number }
export interface NutrientAmount { code: NutrientCode; name: string; category: NutrientCategory; amount: number; unit: NutrientUnit; confidence: number | null; provenance: NutrientProvenance }
