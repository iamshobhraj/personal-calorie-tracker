import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../api/errors";
import { Alert } from "../components/Alert";
import { Button } from "../components/Button";
import { useToast } from "../components/ToastProvider";
import { uploadPdf } from "../features/pdf-import/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useProfileTimezone } from "../hooks/useProfileTimezone";

export function PdfImportsPage(): React.JSX.Element {
  useDocumentTitle("Bulk PDF Diary Import");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const timezone = useProfileTimezone();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const handleFileChange = (selected: File | null) => {
    if (!selected) return;
    if (selected.size > 15 * 1024 * 1024) {
      setError("PDF files must be 15 MiB or smaller.");
      return;
    }
    setError(null);
    setFile(selected);
  };

  const submit = async (): Promise<void> => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadPdf(file, timezone);
      showToast("PDF parsed successfully! Review the extracted rows below.", "success");
      navigate(`/imports/${result.data.id}`);
    } catch (reason) {
      if (reason instanceof ApiError && reason.code === "PDF_DAILY_LIMIT") {
        setError("Today's PDF preview limit has been reached. Please try again tomorrow.");
      } else {
        setError("The PDF could not be processed. Ensure the document contains readable tabular text.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="page-container page-container--narrow">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Bulk PDF Import <span className="beta-badge">Bonus</span>
          </h1>
          <p className="page-subtitle">
            Upload a meal diary or nutrition history PDF to preview and bulk-log entries into your tracker.
          </p>
        </div>
      </div>

      <section className="card form-layout">
        <div className="pdf-upload-dropzone upload-dropzone">
          {file ? (
            <div className="pdf-file-selected">
              <span className="pdf-icon">📄</span>
              <strong className="pdf-filename">{file.name}</strong>
              <span className="pdf-filesize">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </span>
              <Button
                type="button"
                variant="outline"
                size="small"
                onClick={() => setFile(null)}
                disabled={isUploading}
              >
                Change PDF
              </Button>
            </div>
          ) : (
            <label className="dropzone-label">
              <span className="dropzone-icon">📋</span>
              <span className="dropzone-text">Click or drag & drop your food diary PDF</span>
              <span className="dropzone-hint">Supports tabular diary PDFs up to 15 MB</span>
              <input
                aria-label="Upload diary PDF"
                type="file"
                accept="application/pdf,.pdf"
                className="visually-hidden"
                disabled={isUploading}
                onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
              />
            </label>
          )}
        </div>

        <div className="pdf-info-banner">
          <div className="pdf-info-icon">ℹ️</div>
          <div>
            <strong>How bulk import works:</strong>
            <p className="form-subtitle">
              Your document is securely processed inline for structured preview extraction, and deleted immediately from temporary storage. You can inspect, edit, and select which rows to commit into your diary.
            </p>
          </div>
        </div>

        {error && <Alert>{error}</Alert>}

        <div className="form-actions">
          <div className="form-actions__left" />
          <div className="form-actions__right">
            <Button
              type="button"
              variant="primary"
              size="large"
              disabled={!file || isUploading}
              isLoading={isUploading}
              onClick={() => void submit()}
            >
              {isUploading ? "Extracting Diary Rows with AI…" : "🔍 Parse & Preview PDF"}
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
