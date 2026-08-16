import { useState } from "react";
import type { Goal } from "../../api/contracts/goals";
import { Button } from "../../components/Button";
import { ConfirmDialog } from "../../components/ConfirmDialog";

type GoalCardProps = {
  goal: Goal;
  onArchive(id: string): void;
  archiving: boolean;
};

function formatTargetName(code: string): string {
  switch (code) {
    case "ENERGY_KCAL":
      return "Energy";
    case "PROTEIN":
      return "Protein";
    case "CARBOHYDRATE":
      return "Carbs";
    case "FAT":
      return "Fat";
    default:
      return code.replaceAll("_", " ");
  }
}

export function GoalCard({ goal, onArchive, archiving }: GoalCardProps): React.JSX.Element {
  const [showConfirm, setShowConfirm] = useState(false);

  return (
    <>
      <article className="card goal-card">
        <div className="goal-card__header">
          <div>
            <div className="goal-card__badge-row">
              <span className={`status-badge status-badge--${goal.status.toLowerCase()}`}>
                {goal.status}
              </span>
              <span className="goal-card__dates">
                🗓️ {goal.effectiveFrom} {goal.effectiveTo ? `→ ${goal.effectiveTo}` : "onward"}
              </span>
            </div>
            <h3 className="goal-card__title">{goal.name}</h3>
            {goal.targetWeightKg && (
              <p className="goal-card__weight">
                🎯 Target Weight: <strong>{goal.targetWeightKg} kg</strong>
              </p>
            )}
          </div>

          <Button
            variant="outline"
            size="small"
            className="btn--danger-outline"
            disabled={archiving}
            onClick={() => setShowConfirm(true)}
            type="button"
          >
            Archive Goal
          </Button>
        </div>

        <div className="goal-card__targets">
          <span className="goal-card__targets-label">Daily Targets:</span>
          <div className="targets-grid">
            {goal.targets.map((target) => (
              <div key={target.nutrientCode} className="target-pill">
                <span className="target-pill__name">{formatTargetName(target.nutrientCode)}</span>
                <strong className="target-pill__amount">
                  {target.targetAmount} {target.unit}
                </strong>
                <span className="target-pill__kind">({target.targetKind.toLowerCase()})</span>
              </div>
            ))}
          </div>
        </div>
      </article>

      <ConfirmDialog
        open={showConfirm}
        title="Archive this health goal?"
        description={`Are you sure you want to archive "${goal.name}"? Historical reports will preserve this goal, but it will no longer be your active daily target.`}
        confirmLabel="Archive"
        variant="danger"
        isLoading={archiving}
        onConfirm={() => {
          setShowConfirm(false);
          onArchive(goal.id);
        }}
        onCancel={() => setShowConfirm(false)}
      />
    </>
  );
}
