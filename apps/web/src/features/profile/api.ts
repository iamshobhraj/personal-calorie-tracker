import { apiRequest } from "../../api/client"; import type { ProfileUpdateInput } from "../../api/contracts/profile"; import { envelopeSchema } from "../../api/schemas/common"; import { profileSchema } from "../../api/schemas/resources";
export const getProfile = () => apiRequest("/profile", { schema: envelopeSchema(profileSchema) });
export const updateProfile = (input: ProfileUpdateInput) => apiRequest("/profile", { method: "PUT", body: input, schema: envelopeSchema(profileSchema) });
