import { CheckCircle2, AlertCircle, HelpCircle } from "lucide-react";
import type { MicronutrientSummary } from "../api/contracts/reports";

interface MicronutrientChartProps {
  data: MicronutrientSummary[];
}

export function MicronutrientChart({ data }: MicronutrientChartProps): React.JSX.Element {
  if (data.length === 0) {
    return (
      <div className="loading-placeholder">
        No micronutrient data recorded for the selected period.
      </div>
    );
  }

  return (
    <div className="micros-container">
      <div className="micros-grid">
        {data.map((item) => {
          const coverage = Math.min(100, Math.round(item.coveragePercent));
          const dailyAvg = item.dailyAverage !== null ? Math.round(item.dailyAverage * 10) / 10 : null;
          const totalAmt = item.amount !== null ? Math.round(item.amount * 10) / 10 : null;

          let statusBadgeClass = "micro-badge--neutral";
          let statusText = "Recorded";
          let StatusIcon = HelpCircle;

          if (coverage >= 80) {
            statusBadgeClass = "micro-badge--good";
            statusText = "Optimal";
            StatusIcon = CheckCircle2;
          } else if (coverage >= 40) {
            statusBadgeClass = "micro-badge--warning";
            statusText = "Moderate";
            StatusIcon = AlertCircle;
          }

          return (
            <div key={item.nutrientCode} className="micro-card">
              <div className="micro-card__header">
                <div>
                  <h4 className="micro-card__name">{item.name}</h4>
                  <span className="micro-card__code">{item.nutrientCode}</span>
                </div>
                <span className={`micro-badge ${statusBadgeClass}`}>
                  <StatusIcon size={12} /> {statusText}
                </span>
              </div>

              <div className="micro-card__stats">
                <div className="micro-stat">
                  <span className="micro-stat__label">Daily Avg</span>
                  <span className="micro-stat__value">
                    {dailyAvg !== null ? `${dailyAvg} ${item.unit}` : "—"}
                  </span>
                </div>
                <div className="micro-stat micro-stat--right">
                  <span className="micro-stat__label">Total Period</span>
                  <span className="micro-stat__value">
                    {totalAmt !== null ? `${totalAmt} ${item.unit}` : "—"}
                  </span>
                </div>
              </div>

              <div className="micro-card__progress-container">
                <div className="micro-card__progress-bar">
                  <div
                    className="micro-card__progress-fill"
                    style={{
                      width: `${coverage}%`,
                      backgroundColor:
                        coverage >= 80 ? "#10b981" : coverage >= 40 ? "#f59e0b" : "#94a3b8",
                    }}
                  />
                </div>
                <span className="micro-card__progress-text">{coverage}% days covered</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
