import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import type { ChatSession } from "../api/contracts/chat";
import { Button } from "../components/Button";
import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { createChatSession, listChatSessions } from "../features/chat/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function ChatPage(): React.JSX.Element {
  useDocumentTitle("Nutrition Assistant");
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    setIsLoading(true);
    void listChatSessions()
      .then((value) => {
        if (mounted) {
          setSessions(value.data);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setSessions([]);
          setIsLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const handleStartNewChat = async (): Promise<void> => {
    setIsCreating(true);
    try {
      const session = await createChatSession();
      navigate(`/chat/${session.data.id}`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="page-container page-container--narrow">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Nutrition Assistant <span className="beta-badge">Beta</span>
          </h1>
          <p className="page-subtitle">
            Chat in natural language to log meals, check your calorie goals, and ask nutrition questions.
          </p>
        </div>
        <Button
          variant="primary"
          isLoading={isCreating}
          onClick={() => void handleStartNewChat()}
        >
          ➕ Start New Chat
        </Button>
      </div>

      <div className="chat-intro-card card">
        <div className="chat-intro-icon">💡</div>
        <div>
          <h3>What can you ask?</h3>
          <ul className="chat-intro-list">
            <li>"Log 2 boiled eggs and 1 slice of whole wheat toast for breakfast"</li>
            <li>"How many calories have I consumed today?"</li>
            <li>"Show my current macro goals"</li>
            <li>"Give me 3 high-protein snack ideas under 200 kcal"</li>
          </ul>
        </div>
      </div>

      <section className="chat-history-section">
        <h2 className="section-title">Previous Conversations</h2>
        {isLoading ? (
          <LoadingState />
        ) : sessions.length > 0 ? (
          <div className="chat-sessions-grid">
            {sessions.map((session) => (
              <Link
                key={session.id}
                to={`/chat/${session.id}`}
                className="chat-session-card card"
              >
                <div className="chat-session-card__title">
                  💬 {session.title ?? "Nutrition Conversation"}
                </div>
                <span className="chat-session-card__date">
                  {new Date(session.updatedAt).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState>
            <p>No chat history yet. Start a new conversation above!</p>
          </EmptyState>
        )}
      </section>
    </div>
  );
}
