import type { NutritionExtraction } from "../../api/contracts/extractions";
import { Alert } from "../../components/Alert";
import { MealForm } from "../meals/MealForm";

export function ExtractionPreview({ extraction }: { extraction: NutritionExtraction }): React.JSX.Element {
  if (extraction.status !== "SUCCEEDED" || extraction.result === null) {
    return <Alert>{extraction.failure?.message ?? "The image could not be analyzed."}</Alert>;
  }

  return (
    <section>
      <Alert>
        {extraction.result.imageKind === "PLATE"
          ? "Plate estimates are approximate and require your review."
          : "Review the transcribed label before saving."}
      </Alert>
      <h2>{extraction.result.foodName}</h2>
      {extraction.result.warnings.map((warning) => (
        <p key={warning}>{warning}</p>
      ))}
      <MealForm extraction={extraction.result} extractionId={extraction.id} />
    </section>
  );
}
