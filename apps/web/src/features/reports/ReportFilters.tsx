import { Calendar, Clock } from "lucide-react";
import { localDateString } from "../../utils/zonedDateTime";

interface ReportFiltersProps {
  from: string;
  to: string;
  onFrom(value: string): void;
  onTo(value: string): void;
  timezone: string;
}

export function ReportFilters({
  from,
  to,
  onFrom,
  onTo,
  timezone,
}: ReportFiltersProps): React.JSX.Element {
  const setPreset = (days: number) => {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - (days - 1));
    onFrom(localDateString(start, timezone));
    onTo(localDateString(today, timezone));
  };

  const setThisMonth = () => {
    const today = new Date();
    const start = new Date(today.getFullYear(), today.getMonth(), 1);
    onFrom(localDateString(start, timezone));
    onTo(localDateString(today, timezone));
  };

  const isPresetActive = (days: number) => {
    const today = new Date();
    const start = new Date(today);
    start.setDate(today.getDate() - (days - 1));
    return from === localDateString(start, timezone) && to === localDateString(today, timezone);
  };

  const isMonthActive = () => {
    const today = new Date();
    const start = new Date(today.getFullYear(), today.getMonth(), 1);
    return from === localDateString(start, timezone) && to === localDateString(today, timezone);
  };

  return (
    <div className="reports-filters-container card">
      <div className="reports-presets">
        <span className="reports-presets__label">
          <Clock size={15} /> Range:
        </span>
        <button
          type="button"
          className={`filter-btn ${isPresetActive(7) ? "filter-btn--active" : ""}`}
          onClick={() => setPreset(7)}
        >
          7 Days
        </button>
        <button
          type="button"
          className={`filter-btn ${isPresetActive(14) ? "filter-btn--active" : ""}`}
          onClick={() => setPreset(14)}
        >
          14 Days
        </button>
        <button
          type="button"
          className={`filter-btn ${isPresetActive(30) ? "filter-btn--active" : ""}`}
          onClick={() => setPreset(30)}
        >
          30 Days
        </button>
        <button
          type="button"
          className={`filter-btn ${isMonthActive() ? "filter-btn--active" : ""}`}
          onClick={setThisMonth}
        >
          This Month
        </button>
      </div>

      <div className="reports-date-inputs">
        <div className="reports-date-field">
          <span className="reports-date-label">From:</span>
          <div className="input-with-icon">
            <Calendar size={14} className="input-icon-left" />
            <input
              type="date"
              className="reports-date-input"
              value={from}
              onChange={(e) => onFrom(e.target.value)}
            />
          </div>
        </div>

        <div className="reports-date-field">
          <span className="reports-date-label">To:</span>
          <div className="input-with-icon">
            <Calendar size={14} className="input-icon-left" />
            <input
              type="date"
              className="reports-date-input"
              value={to}
              onChange={(e) => onTo(e.target.value)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
