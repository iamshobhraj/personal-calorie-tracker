import type { NutritionExtraction } from "../../api/contracts/extractions";
import { Alert } from "../../components/Alert";
import { MealForm } from "../meals/MealForm";
export function ExtractionPreview({ extraction }: { extraction: NutritionExtraction }): React.JSX.Element { return extraction.status !== "SUCCEEDED" || extraction.result === null ? <Alert>{extraction.failure?.message ?? "The image could not be analyzed."}</Alert> : <section><Alert>{extraction.result.imageKind === "PLATE" ? "Plate estimates are approximate and require your review." : "Review the transcribed label before saving."}</Alert><h2>{extraction.result.foodName}</h2>{extraction.result.warnings.map(warning => <p key={warning}>{warning}</p>)}<MealForm extractionId={extraction.id} /></section>; }
