import type { GoalStatus, IsoDate, IsoDateTime, NutrientCode, NutrientUnit, TargetKind, UUID } from "./common";
export interface GoalTarget { nutrientCode: NutrientCode; targetAmount: number; unit: NutrientUnit; targetKind: TargetKind }
export interface Goal { id: UUID; name: string; effectiveFrom: IsoDate; effectiveTo: IsoDate | null; targetWeightKg: number | null; status: GoalStatus; targets: GoalTarget[]; createdAt: IsoDateTime; updatedAt: IsoDateTime }
export interface GoalTargetInput { nutrientCode: NutrientCode; targetAmount: number; targetKind: TargetKind }
export interface GoalCreateInput { name: string; effectiveFrom: IsoDate; effectiveTo?: IsoDate | null; targetWeightKg?: number | null; targets: GoalTargetInput[] }
