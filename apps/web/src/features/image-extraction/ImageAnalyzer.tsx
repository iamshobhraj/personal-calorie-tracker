import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import type { ImageKind } from "../../api/contracts/common";
import type { NutritionExtraction } from "../../api/contracts/extractions";
import { Alert } from "../../components/Alert";
import { Button } from "../../components/Button";
import { ExtractionPreview } from "./ExtractionPreview";
import { analyzeImage } from "./api";

const imageKinds: { value: ImageKind; label: string; desc: string }[] = [
  { value: "AUTO", label: "Auto Detect", desc: "Automatically determine plate vs nutrition label" },
  { value: "PLATE", label: "Food Plate", desc: "Estimate calories and macros from cooked meal photo" },
  { value: "LABEL", label: "Nutrition Label", desc: "Transcribe packaged food nutrition fact tables" },
];

export function ImageAnalyzer(): React.JSX.Element {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [kind, setKind] = useState<ImageKind>("AUTO");
  const [extraction, setExtraction] = useState<NutritionExtraction | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      if (!file) return Promise.reject(new Error("Please select an image first."));
      return analyzeImage(file, kind);
    },
    onSuccess: (data) => {
      setExtraction(data.data);
    },
  });

  const handleFileChange = (selected: File | null) => {
    if (!selected) return;
    if (selected.size > 10 * 1024 * 1024) {
      alert("Image must be 10 MiB or smaller.");
      return;
    }
    setFile(selected);
    setExtraction(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(typeof e.target?.result === "string" ? e.target.result : null);
    };
    reader.readAsDataURL(selected);
  };

  const handleReset = () => {
    setFile(null);
    setPreviewUrl(null);
    setExtraction(null);
  };

  return (
    <div className="analyzer-container">
      {!extraction ? (
        <section className="card analyzer-card">
          <div className="analyzer-card__header">
            <h2>Scan Food or Nutrition Label</h2>
            <p className="form-subtitle">
              Upload a meal photo or food nutrition label. Gemini Vision AI will analyze calories and nutrients for your review.
            </p>
          </div>

          <div className="upload-dropzone">
            {previewUrl ? (
              <div className="image-preview-box">
                <img src={previewUrl} alt="Upload preview" className="image-preview-box__img" />
                <Button
                  type="button"
                  variant="outline"
                  size="small"
                  onClick={handleReset}
                  className="image-preview-box__change-btn"
                >
                  Change Image
                </Button>
              </div>
            ) : (
              <label className="dropzone-label">
                <span className="dropzone-icon">📷</span>
                <span className="dropzone-text">Click or drag & drop a photo here</span>
                <span className="dropzone-hint">Supports JPEG, PNG, WebP up to 10 MB</span>
                <input
                  aria-label="Upload nutrition image"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="visually-hidden"
                  onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
                />
              </label>
            )}
          </div>

          <div className="analyzer-options">
            <label className="field">
              <span>Analysis Mode</span>
              <select
                value={kind}
                onChange={(e) => setKind(e.target.value as ImageKind)}
              >
                {imageKinds.map((k) => (
                  <option key={k.value} value={k.value}>
                    {k.label} — {k.desc}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {mutation.isError && (
            <Alert>
              The image could not be analyzed. Please ensure the image is clear and try again, or enter the meal manually.
            </Alert>
          )}

          <div className="analyzer-actions">
            <Button
              type="button"
              variant="primary"
              size="large"
              disabled={!file || mutation.isPending}
              isLoading={mutation.isPending}
              onClick={() => mutation.mutate()}
            >
              {mutation.isPending ? "Analyzing with Gemini AI…" : "🔍 Extract Nutrition Details"}
            </Button>
          </div>
        </section>
      ) : (
        <div className="extraction-result-wrap">
          <div className="extraction-result-topbar">
            <Button variant="outline" size="small" onClick={handleReset}>
              ← Scan Another Image
            </Button>
          </div>
          <ExtractionPreview extraction={extraction} />
        </div>
      )}
    </div>
  );
}
