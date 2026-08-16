import { Button } from "../../components/Button";
import { Field } from "../../components/Field";

interface MealFiltersProps {
  dateFrom: string;
  dateTo: string;
  onDateFrom(value: string): void;
  onDateTo(value: string): void;
  onRangeChange?(from: string, to: string): void;
}

export function MealFilters({
  dateFrom,
  dateTo,
  onDateFrom,
  onDateTo,
  onRangeChange,
}: MealFiltersProps): React.JSX.Element {
  const setRange = (from: string, to: string) => {
    if (onRangeChange) {
      onRangeChange(from, to);
    } else {
      onDateFrom(from);
      onDateTo(to);
    }
  };

  const setToday = () => {
    const today = new Date().toISOString().slice(0, 10);
    setRange(today, today);
  };

  const setYesterday = () => {
    const d = new Date();
    d.setDate(d.getDate() - 1);
    const yesterday = d.toISOString().slice(0, 10);
    setRange(yesterday, yesterday);
  };

  const setLast7Days = () => {
    const today = new Date();
    const past = new Date();
    past.setDate(today.getDate() - 6);
    setRange(past.toISOString().slice(0, 10), today.toISOString().slice(0, 10));
  };

  const todayStr = new Date().toISOString().slice(0, 10);
  const isToday = dateFrom === todayStr && dateTo === todayStr;

  return (
    <div className="meal-filters card">
      <div className="filter-presets">
        <span className="filter-label">Quick filter:</span>
        <Button
          type="button"
          size="small"
          variant={isToday ? "primary" : "outline"}
          onClick={setToday}
        >
          Today
        </Button>
        <Button
          type="button"
          size="small"
          variant="outline"
          onClick={setYesterday}
        >
          Yesterday
        </Button>
        <Button
          type="button"
          size="small"
          variant="outline"
          onClick={setLast7Days}
        >
          Last 7 Days
        </Button>
      </div>

      <div className="filter-dates">
        <Field
          label="From date"
          type="date"
          value={dateFrom}
          onChange={(e) => onDateFrom(e.target.value)}
        />
        <Field
          label="To date"
          type="date"
          value={dateTo}
          onChange={(e) => onDateTo(e.target.value)}
        />
      </div>
    </div>
  );
}
