import { apiRequest } from "../../api/client";
import { pageSchema } from "../../api/schemas/common";
import { calorieTrendSchema, macroSchema, micronutrientSchema } from "../../api/schemas/reports";
export const reports = (query: string) => ({ calories: apiRequest(`/reports/calorie-trend?${query}`, { schema: pageSchema(calorieTrendSchema) }), macros: apiRequest(`/reports/macros?${query}`, { schema: pageSchema(macroSchema) }), micronutrients: apiRequest(`/reports/micronutrients?${query}`, { schema: pageSchema(micronutrientSchema) }) });
