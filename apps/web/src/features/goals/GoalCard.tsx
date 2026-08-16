import type { Goal } from "../../api/contracts/goals";
import { Button } from "../../components/Button";

type GoalCardProps = {
  goal: Goal;
  onArchive(id: string): void;
  archiving: boolean;
};

export function GoalCard({ goal, onArchive, archiving }: GoalCardProps): React.JSX.Element {
  return (
    <article className="card">
      <div className="row">
        <h2>{goal.name}</h2>
        <Button disabled={archiving} onClick={() => onArchive(goal.id)} type="button">
          {archiving ? "Archiving…" : "Archive"}
        </Button>
      </div>
      <p>
        {goal.effectiveFrom}
        {goal.effectiveTo ? ` to ${goal.effectiveTo}` : " onward"}
      </p>
      <ul>
        {goal.targets.map((target) => (
          <li key={target.nutrientCode}>
            {target.nutrientCode}: {target.targetAmount} {target.unit}
          </li>
        ))}
      </ul>
    </article>
  );
}
