import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getPdfImport } from "../features/pdf-import/api";
export function PdfImportReviewPage(): React.JSX.Element { const { importId = "" } = useParams(); const [summary, setSummary] = useState<string>("Loading preview…"); useEffect(() => { void getPdfImport(importId).then(result => setSummary(`${result.data.status}: ${result.data.summary.validRows} valid, ${result.data.summary.invalidRows} invalid`)).catch(() => setSummary("Preview is unavailable.")); }, [importId]); return <section><h1>Review PDF import</h1><p>{summary}</p><p>Review each row before commit. No direct import is performed.</p></section>; }
