import { apiRequest } from "../../api/client"; import { pageSchema } from "../../api/schemas/common"; import { nutrientSchema } from "../../api/schemas/resources";
export const getNutrients = () => apiRequest("/nutrients?page=1&limit=100", { schema: pageSchema(nutrientSchema) });
