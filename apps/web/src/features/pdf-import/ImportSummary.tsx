import type { PdfImportSummary } from "../../api/contracts/pdfImports";
export function ImportSummary({ summary }: { summary: PdfImportSummary }): React.JSX.Element { return <p>{summary.validRows} valid / {summary.invalidRows} invalid of {summary.totalRows}</p>; }
