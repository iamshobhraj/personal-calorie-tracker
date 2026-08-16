import { ImageAnalyzer } from "../features/image-extraction/ImageAnalyzer";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function AnalyzeImagePage(): React.JSX.Element {
  useDocumentTitle("AI Food & Label Scanner");
  return (
    <div className="page-container page-container--narrow">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Nutrition Scanner</h1>
          <p className="page-subtitle">
            Upload food plate photos or nutrition fact labels for automated macro and calorie extraction.
          </p>
        </div>
      </div>
      <ImageAnalyzer />
    </div>
  );
}
