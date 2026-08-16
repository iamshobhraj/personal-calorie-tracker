import { useState, type KeyboardEvent } from "react";
import { Button } from "../../components/Button";

interface ChatComposerProps {
  onSend(message: string): Promise<void>;
  isLoading: boolean;
  disabled?: boolean;
}

const starterPrompts = [
  "Log 2 boiled eggs and 1 slice of whole wheat toast for breakfast",
  "How many calories have I logged today?",
  "What is my current health goal?",
  "Suggest a high-protein lunch around 500 kcal",
];

export function ChatComposer({
  onSend,
  isLoading,
  disabled = false,
}: ChatComposerProps): React.JSX.Element {
  const [message, setMessage] = useState("");

  const handleSubmit = async () => {
    const trimmed = message.trim();
    if (!trimmed || isLoading || disabled) return;
    setMessage("");
    await onSend(trimmed);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSubmit();
    }
  };

  const handleSelectPrompt = (prompt: string) => {
    setMessage(prompt);
  };

  return (
    <div className="chat-composer-wrap">
      <div className="chat-prompt-chips">
        <span className="chips-label">Suggestions:</span>
        {starterPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className="chip-btn"
            onClick={() => handleSelectPrompt(prompt)}
            disabled={isLoading || disabled}
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-composer-box">
        <textarea
          className="chat-composer-textarea"
          placeholder="Ask a nutrition question or say 'Log 1 cup of oats for breakfast'… (Press Enter to send)"
          rows={2}
          maxLength={2000}
          value={message}
          disabled={isLoading || disabled}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <Button
          type="button"
          variant="primary"
          className="chat-send-btn"
          disabled={!message.trim() || isLoading || disabled}
          isLoading={isLoading}
          onClick={() => void handleSubmit()}
        >
          Send
        </Button>
      </div>
    </div>
  );
}
