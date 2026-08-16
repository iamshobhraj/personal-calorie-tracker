import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import type { MealType, NutrientCode } from "../api/contracts/common";
import type { MealNutrientInput, MealUpsertInput } from "../api/contracts/meals";
import { Alert } from "../components/Alert";
import { Button } from "../components/Button";
import { Field } from "../components/Field";
import { LoadingState } from "../components/LoadingState";
import { useToast } from "../components/ToastProvider";
import {
  commitPdfImport,
  getPdfImport,
  getPdfRows,
  updatePdfRow,
} from "../features/pdf-import/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { localDateTimeInput, offsetDateTime } from "../utils/zonedDateTime";

const mealTypes: MealType[] = ["BREAKFAST", "LUNCH", "DINNER", "SNACKS"];

type EditableRow = {
  rowId: number;
  sourceRowNumber: number;
  selected: boolean;
  foodName: string;
  mealType: MealType;
  quantity: number;
  unit: string;
  description: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  occurredAt: string;
  timezone: string;
  notes: string;
  nutrients: MealNutrientInput[];
  validationErrors: string[];
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function numberValue(value: unknown, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function dateTimeInput(value: unknown, timezone: string): string {
  if (typeof value === "string" && value) {
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.valueOf())) return localDateTimeInput(parsed, timezone);
  }
  return localDateTimeInput(new Date(), timezone);
}

function editableRow(value: {
  rowId: number;
  sourceRowNumber: number;
  selected: boolean;
  parsedMeal: unknown;
  validationErrors: unknown[];
}): EditableRow {
  const meal = isRecord(value.parsedMeal) ? value.parsedMeal : {};
  const quantity = isRecord(meal.quantity) ? meal.quantity : {};
  const nutrients = Array.isArray(meal.nutrients)
    ? meal.nutrients.filter(isRecord).map((nutrient) => ({
        code: String(nutrient.code) as NutrientCode,
        amount: numberValue(nutrient.amount, 0),
        confidence: numberValue(nutrient.confidence, 0),
      }))
    : [];

  const errors = value.validationErrors
    .filter(isRecord)
    .map((error) => (typeof error.message === "string" ? error.message : "Invalid row data."));

  const mealType = mealTypes.includes(meal.mealType as MealType)
    ? (meal.mealType as MealType)
    : "LUNCH";

  const timezone =
    typeof meal.timezone === "string"
      ? meal.timezone
      : Intl.DateTimeFormat().resolvedOptions().timeZone;

  const cal = nutrients.find((n) => n.code === "ENERGY_KCAL")?.amount ?? 0;
  const p = nutrients.find((n) => n.code === "PROTEIN")?.amount ?? 0;
  const c = nutrients.find((n) => n.code === "CARBOHYDRATE")?.amount ?? 0;
  const f = nutrients.find((n) => n.code === "FAT")?.amount ?? 0;

  return {
    rowId: value.rowId,
    sourceRowNumber: value.sourceRowNumber,
    selected: value.selected,
    foodName: typeof meal.foodName === "string" ? meal.foodName : "",
    mealType,
    quantity: numberValue(quantity.value, 1),
    unit: typeof quantity.unit === "string" ? quantity.unit : "serving",
    description: typeof quantity.description === "string" ? quantity.description : "",
    calories: cal,
    protein: p,
    carbs: c,
    fat: f,
    occurredAt: dateTimeInput(meal.occurredAt, timezone),
    timezone,
    notes: typeof meal.notes === "string" ? meal.notes : "",
    nutrients,
    validationErrors: errors,
  };
}

function payload(row: EditableRow): MealUpsertInput {
  const nutrients: MealNutrientInput[] = [
    { code: "ENERGY_KCAL", amount: row.calories || 0 },
  ];
  if (row.protein > 0) nutrients.push({ code: "PROTEIN", amount: row.protein });
  if (row.carbs > 0) nutrients.push({ code: "CARBOHYDRATE", amount: row.carbs });
  if (row.fat > 0) nutrients.push({ code: "FAT", amount: row.fat });

  return {
    mealType: row.mealType,
    foodName: row.foodName.trim(),
    quantity: {
      value: row.quantity || 1,
      unit: row.unit.trim() || "serving",
      description: row.description.trim() || null,
    },
    occurredAt: offsetDateTime(row.occurredAt, row.timezone),
    timezone: row.timezone,
    source: "PDF",
    sourceExtractionId: null,
    notes: row.notes.trim() || null,
    nutrients,
  };
}

export function PdfImportReviewPage(): React.JSX.Element {
  useDocumentTitle("Review PDF Import");
  const { importId = "" } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();

  const [importStatus, setImportStatus] = useState<string>("PROCESSING");
  const [summaryStats, setSummaryStats] = useState({ totalRows: 0, validRows: 0, invalidRows: 0 });
  const [rows, setRows] = useState<EditableRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingRow, setSavingRow] = useState<number | null>(null);
  const [committing, setCommitting] = useState(false);
  const [committed, setCommitted] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    try {
      const [item, rowPage] = await Promise.all([getPdfImport(importId), getPdfRows(importId)]);
      setImportStatus(item.data.status);
      setSummaryStats(item.data.summary);
      setRows(rowPage.data.map(editableRow));
      setError(null);
    } catch {
      setError("The PDF import preview could not be loaded.");
    } finally {
      setLoading(false);
    }
  }, [importId]);

  useEffect(() => {
    void load();
  }, [load]);

  const updateRow = (rowId: number, update: Partial<EditableRow>): void => {
    setRows((items) => items.map((row) => (row.rowId === rowId ? { ...row, ...update } : row)));
  };

  const save = async (row: EditableRow): Promise<void> => {
    setSavingRow(row.rowId);
    setError(null);
    try {
      await updatePdfRow(importId, row.rowId, row.selected, payload(row));
      showToast(`Row ${row.sourceRowNumber} updated`, "success");
      await load();
    } catch {
      setError(`Row ${row.sourceRowNumber} could not be saved. Check required fields.`);
    } finally {
      setSavingRow(null);
    }
  };

  const selectAll = (select: boolean) => {
    setRows((items) => items.map((r) => ({ ...r, selected: select })));
  };

  const commit = async (): Promise<void> => {
    setCommitting(true);
    setError(null);
    try {
      const selectedValidRows = rows.filter(
        (row) => row.selected && row.validationErrors.length === 0
      );
      const result = await commitPdfImport(
        importId,
        selectedValidRows.map((row) => row.rowId)
      );
      showToast(
        `Successfully logged ${result.data.createdCount} meal${result.data.createdCount === 1 ? "" : "s"} to your diary!`,
        "success"
      );
      setCommitted(`${result.data.createdCount} meal${result.data.createdCount === 1 ? "" : "s"} added to diary.`);
      await load();
      navigate("/meals");
    } catch {
      setError("Selected rows could not be committed. Please fix any invalid rows or deselect them.");
    } finally {
      setCommitting(false);
    }
  };

  if (loading) return <LoadingState />;

  const validSelectedCount = rows.filter(
    (row) => row.selected && row.validationErrors.length === 0
  ).length;

  return (
    <div className="page-container">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <Link to="/imports">← Back to PDF Imports</Link>
      </nav>

      <div className="page-header">
        <div>
          <h1 className="page-title">Review Extracted Diary Rows</h1>
          <p className="page-subtitle">
            Inspect each parsed meal row, edit nutritional values as needed, and commit valid entries into your diary.
          </p>
        </div>
      </div>

      {/* Summary Stat Bar */}
      <div className="summary-bar card">
        <div className="summary-stat">
          <span className="summary-stat__label">Import Status</span>
          <strong className="summary-stat__value">{importStatus}</strong>
        </div>
        <div className="summary-stat">
          <span className="summary-stat__label">Total Parsed Rows</span>
          <strong className="summary-stat__value">{summaryStats.totalRows}</strong>
        </div>
        <div className="summary-stat">
          <span className="summary-stat__label">Valid Rows</span>
          <strong className="summary-stat__value" style={{ color: "var(--brand-dark)" }}>
            {summaryStats.validRows}
          </strong>
        </div>
        {summaryStats.invalidRows > 0 && (
          <div className="summary-stat">
            <span className="summary-stat__label">Needs Attention</span>
            <strong className="summary-stat__value" style={{ color: "var(--danger)" }}>
              {summaryStats.invalidRows}
            </strong>
          </div>
        )}
      </div>

      {error && <Alert>{error}</Alert>}
      {committed && <div className="alert toast--success">{committed}</div>}

      {/* Action Toolbar */}
      <div className="pdf-actions-bar card">
        <div className="pdf-actions-bar__left">
          <Button type="button" variant="outline" size="small" onClick={() => selectAll(true)}>
            Select All
          </Button>
          <Button type="button" variant="outline" size="small" onClick={() => selectAll(false)}>
            Deselect All
          </Button>
        </div>
        <div className="pdf-actions-bar__right">
          <Button
            type="button"
            variant="primary"
            disabled={committing || validSelectedCount === 0 || importStatus === "COMMITTED"}
            isLoading={committing}
            onClick={() => void commit()}
          >
            {importStatus === "COMMITTED"
              ? "✓ Already Committed"
              : `Commit ${validSelectedCount} Selected Meal${validSelectedCount === 1 ? "" : "s"} to Diary`}
          </Button>
        </div>
      </div>

      {/* Rows List */}
      <div className="pdf-rows-list">
        {rows.map((row) => {
          const isValid = row.validationErrors.length === 0;

          return (
            <article
              key={row.rowId}
              className={`card pdf-row-card ${!isValid ? "pdf-row-card--invalid" : ""}`}
            >
              <div className="pdf-row-card__header">
                <label className="pdf-row-checkbox-label">
                  <input
                    checked={row.selected}
                    type="checkbox"
                    onChange={(event) =>
                      updateRow(row.rowId, { selected: event.target.checked })
                    }
                  />
                  <strong>Row #{row.sourceRowNumber}</strong>
                </label>

                <div className="pdf-row-status-badges">
                  {isValid ? (
                    <span className="status-badge status-badge--active">✓ Valid</span>
                  ) : (
                    <span className="badge badge--snacks">⚠️ Needs Correction</span>
                  )}
                </div>
              </div>

              {row.validationErrors.length > 0 && (
                <div className="pdf-row-errors">
                  {row.validationErrors.map((msg) => (
                    <p key={msg} className="warning-item">
                      ⚠️ {msg}
                    </p>
                  ))}
                </div>
              )}

              <div className="form-grid">
                <Field
                  label="Food Name *"
                  value={row.foodName}
                  onChange={(e) => updateRow(row.rowId, { foodName: e.target.value })}
                />

                <label className="field">
                  <span>Meal Type *</span>
                  <select
                    value={row.mealType}
                    onChange={(e) =>
                      updateRow(row.rowId, { mealType: e.target.value as MealType })
                    }
                  >
                    {mealTypes.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="form-row">
                  <Field
                    label="Quantity"
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={row.quantity}
                    onChange={(e) =>
                      updateRow(row.rowId, { quantity: numberValue(e.target.value, 1) })
                    }
                  />
                  <Field
                    label="Unit"
                    value={row.unit}
                    onChange={(e) => updateRow(row.rowId, { unit: e.target.value })}
                  />
                </div>

                <Field
                  label={`When (${row.timezone})`}
                  type="datetime-local"
                  value={row.occurredAt}
                  onChange={(e) => updateRow(row.rowId, { occurredAt: e.target.value })}
                />
              </div>

              {/* Inline Nutrition */}
              <div className="macros-section">
                <div className="macros-grid">
                  <Field
                    label="Calories (kcal)"
                    type="number"
                    min="0"
                    value={row.calories}
                    onChange={(e) =>
                      updateRow(row.rowId, { calories: numberValue(e.target.value, 0) })
                    }
                  />
                  <Field
                    label="Protein (g)"
                    type="number"
                    min="0"
                    value={row.protein}
                    onChange={(e) =>
                      updateRow(row.rowId, { protein: numberValue(e.target.value, 0) })
                    }
                  />
                  <Field
                    label="Carbs (g)"
                    type="number"
                    min="0"
                    value={row.carbs}
                    onChange={(e) =>
                      updateRow(row.rowId, { carbs: numberValue(e.target.value, 0) })
                    }
                  />
                  <Field
                    label="Fat (g)"
                    type="number"
                    min="0"
                    value={row.fat}
                    onChange={(e) =>
                      updateRow(row.rowId, { fat: numberValue(e.target.value, 0) })
                    }
                  />
                </div>
              </div>

              <div className="pdf-row-card__footer">
                <Button
                  type="button"
                  variant="outline"
                  size="small"
                  disabled={savingRow === row.rowId}
                  isLoading={savingRow === row.rowId}
                  onClick={() => void save(row)}
                >
                  Save Row
                </Button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}
