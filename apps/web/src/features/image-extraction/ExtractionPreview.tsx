import type { NutritionExtraction } from "../../api/contracts/extractions";
import { Alert } from "../../components/Alert";
import { MealForm } from "../meals/MealForm";

export function ExtractionPreview({
  extraction,
}: {
  extraction: NutritionExtraction;
}): React.JSX.Element {
  if (extraction.status !== "SUCCEEDED" || extraction.result === null) {
    return (
      <Alert>
        {extraction.failure?.message ?? "The nutrition information could not be extracted from this image."}
      </Alert>
    );
  }

  const result = extraction.result;
  const isPlate = result.imageKind === "PLATE";
  const confidencePercent = Math.round(result.overallConfidence * 100);

  return (
    <div className="extraction-preview-flow">
      <div className="extraction-header-card card">
        <div className="extraction-meta-badges">
          <span className={`badge ${isPlate ? "badge--plate" : "badge--label"}`}>
            {isPlate ? "🍽️ Food Plate Estimation" : "🏷️ Nutrition Label Transcription"}
          </span>
          <span className="badge badge--confidence">
            Confidence: {confidencePercent}%
          </span>
        </div>

        <h2 className="extraction-detected-title">
          Detected: <strong>{result.foodName}</strong>
        </h2>

        <p className="extraction-disclaimer">
          {isPlate
            ? "⚠️ Plate nutrient amounts are estimated from visual portions and may vary based on cooking oils/recipes. Please review and adjust below."
            : "✓ Transcribed from nutrition facts. Verify the serving size below."}
        </p>

        {result.warnings.length > 0 && (
          <div className="extraction-warnings">
            {result.warnings.map((w) => (
              <p key={w} className="warning-item">
                💡 {w}
              </p>
            ))}
          </div>
        )}
      </div>

      <MealForm
        extraction={result}
        extractionId={extraction.id}
        onSuccessRedirect="/meals"
      />
    </div>
  );
}
