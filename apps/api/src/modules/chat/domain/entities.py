from dataclasses import dataclass


@dataclass(frozen=True)
class ChatDraft:
    """A draft is data only; it cannot mutate a meal without confirmation."""

    action: str = "CREATE_MEAL"
