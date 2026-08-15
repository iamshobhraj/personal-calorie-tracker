import { z } from "zod";
export const nutrientCodeSchema = z.enum(["ENERGY_KCAL", "PROTEIN", "CARBOHYDRATE", "FAT", "FIBER", "SUGAR", "VITAMIN_A", "VITAMIN_C", "VITAMIN_D", "VITAMIN_E", "VITAMIN_K", "THIAMIN_B1", "RIBOFLAVIN_B2", "NIACIN_B3", "VITAMIN_B6", "FOLATE_B9", "VITAMIN_B12", "CALCIUM", "IRON", "MAGNESIUM", "PHOSPHORUS", "POTASSIUM", "SODIUM", "ZINC", "SELENIUM"]);
export const profileSchema = z.object({ id: z.string().uuid(), email: z.string().email().nullable(), displayName: z.string().nullable(), timezone: z.string() });
export const nutrientSchema = z.object({ code: nutrientCodeSchema, name: z.string(), category: z.enum(["ENERGY", "MACRO", "VITAMIN", "MINERAL"]), unit: z.enum(["kcal", "g", "mg", "mcg"]), displayOrder: z.number() });
export const nutrientAmountSchema = nutrientSchema.pick({ code: true, name: true, category: true, unit: true }).extend({ amount: z.number(), confidence: z.number().nullable(), provenance: z.enum(["USER", "LABEL_AI", "PLATE_AI", "PDF_AI"]) });
