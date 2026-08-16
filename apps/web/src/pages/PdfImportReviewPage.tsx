import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { MealNutrientInput, MealUpsertInput } from "../api/contracts/meals";
import type { MealType, NutrientCode } from "../api/contracts/common";
import {
  commitPdfImport,
  getPdfImport,
  getPdfRows,
  updatePdfRow,
} from "../features/pdf-import/api";
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
    .map((error) => (typeof error.message === "string" ? error.message : "Invalid row."));
  const mealType = mealTypes.includes(meal.mealType as MealType)
    ? (meal.mealType as MealType)
    : "LUNCH";

  const timezone =
    typeof meal.timezone === "string" ? meal.timezone : Intl.DateTimeFormat().resolvedOptions().timeZone;

  return {
    rowId: value.rowId,
    sourceRowNumber: value.sourceRowNumber,
    selected: value.selected,
    foodName: typeof meal.foodName === "string" ? meal.foodName : "",
    mealType,
    quantity: numberValue(quantity.value, 1),
    unit: typeof quantity.unit === "string" ? quantity.unit : "serving",
    description: typeof quantity.description === "string" ? quantity.description : "",
    occurredAt: dateTimeInput(meal.occurredAt, timezone),
    timezone,
    notes: typeof meal.notes === "string" ? meal.notes : "",
    nutrients,
    validationErrors: errors,
  };
}

function payload(row: EditableRow): MealUpsertInput {
  return {
    mealType: row.mealType,
    foodName: row.foodName.trim(),
    quantity: {
      value: row.quantity,
      unit: row.unit.trim(),
      description: row.description.trim() || null,
    },
    occurredAt: offsetDateTime(row.occurredAt, row.timezone),
    timezone: row.timezone,
    source: "PDF",
    sourceExtractionId: null,
    notes: row.notes.trim() || null,
    nutrients: row.nutrients,
  };
}

export function PdfImportReviewPage(): React.JSX.Element {
  const { importId = "" } = useParams();
  const [summary, setSummary] = useState("Loading preview…");
  const [rows, setRows] = useState<EditableRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [savingRow, setSavingRow] = useState<number | null>(null);
  const [committing, setCommitting] = useState(false);
  const [committed, setCommitted] = useState<string | null>(null);

  const load = useCallback(async (): Promise<void> => {
    try {
      const [item, rowPage] = await Promise.all([getPdfImport(importId), getPdfRows(importId)]);
      setSummary(
        `${item.data.status}: ${item.data.summary.validRows} valid, ${item.data.summary.invalidRows} invalid`,
      );
      setRows(rowPage.data.map(editableRow));
      setError(null);
    } catch {
      setSummary("Preview is unavailable.");
      setError("The PDF preview could not be loaded.");
    }
  }, [importId]);

  useEffect(() => {
    void load();
  }, [load]);

  function updateRow(rowId: number, update: Partial<EditableRow>): void {
    setRows((items) => items.map((row) => (row.rowId === rowId ? { ...row, ...update } : row)));
  }

  async function save(row: EditableRow): Promise<void> {
    setSavingRow(row.rowId);
    setError(null);
    try {
      await updatePdfRow(importId, row.rowId, row.selected, payload(row));
      await load();
    } catch {
      setError(`Row ${row.sourceRowNumber} could not be saved. Check its required fields.`);
    } finally {
      setSavingRow(null);
    }
  }

  async function commit(): Promise<void> {
    setCommitting(true);
    setError(null);
    try {
      const result = await commitPdfImport(
        importId,
        rows.filter((row) => row.selected && row.validationErrors.length === 0).map((row) => row.rowId),
      );
      setCommitted(`${result.data.createdCount} meal${result.data.createdCount === 1 ? "" : "s"} created.`);
      await load();
    } catch {
      setError("Selected rows could not be committed. Save each edited row before committing.");
    } finally {
      setCommitting(false);
    }
  }

  return (
    <section>
      <h1>Review PDF import</h1>
      <p>{summary}</p>
      <p>Review, correct, and save each row before committing selected valid rows.</p>
      {error && <p role="alert">{error}</p>}
      {committed && <p role="status">{committed}</p>}
      {rows.map((row) => (
        <article className="card" key={row.rowId}>
          <h2>Source row {row.sourceRowNumber}</h2>
          {row.validationErrors.map((message) => (
            <p key={message} role="alert">{message}</p>
          ))}
          <label>
            <input
              checked={row.selected}
              type="checkbox"
              onChange={(event) => updateRow(row.rowId, { selected: event.target.checked })}
            />{" "}
            Select this row for commit
          </label>
          <label className="field"><span>Food name</span><input value={row.foodName} onChange={(event) => updateRow(row.rowId, { foodName: event.target.value })} /></label>
          <label className="field"><span>Meal type</span><select value={row.mealType} onChange={(event) => updateRow(row.rowId, { mealType: event.target.value as MealType })}>{mealTypes.map((mealType) => <option key={mealType}>{mealType}</option>)}</select></label>
          <label className="field"><span>Quantity</span><input min="0.01" step="0.01" type="number" value={row.quantity} onChange={(event) => updateRow(row.rowId, { quantity: numberValue(event.target.value, 0) })} /></label>
          <label className="field"><span>Unit</span><input value={row.unit} onChange={(event) => updateRow(row.rowId, { unit: event.target.value })} /></label>
          <label className="field"><span>When ({row.timezone})</span><input type="datetime-local" value={row.occurredAt} onChange={(event) => updateRow(row.rowId, { occurredAt: event.target.value })} /></label>
          <p>Nutrients: {row.nutrients.map((nutrient) => `${nutrient.code}: ${nutrient.amount}`).join(", ") || "None detected"}</p>
          <button disabled={savingRow === row.rowId} onClick={() => void save(row)}>{savingRow === row.rowId ? "Saving…" : "Save row"}</button>
        </article>
      ))}
      <button disabled={committing || !rows.some((row) => row.selected && row.validationErrors.length === 0)} onClick={() => void commit()}>{committing ? "Committing…" : "Commit selected rows"}</button>
    </section>
  );
}
