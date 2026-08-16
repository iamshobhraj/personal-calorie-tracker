import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import type { ChatMessage, MealDraftAction as MealDraftActionType } from "../api/contracts/chat";
import { Alert } from "../components/Alert";
import { LoadingState } from "../components/LoadingState";
import { ChatComposer } from "../features/chat/ChatComposer";
import { ChatMessageList } from "../features/chat/ChatMessageList";
import { listChatMessages, sendChatMessage } from "../features/chat/api";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useProfileTimezone } from "../hooks/useProfileTimezone";
import { generateUuid } from "../utils/uuid";

export function ChatSessionPage(): React.JSX.Element {
  useDocumentTitle("Nutrition Assistant Chat");
  const { sessionId = "" } = useParams();
  const timezone = useProfileTimezone();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setIsLoading(true);
    setError(null);

    void listChatMessages(sessionId)
      .then((res) => {
        if (mounted) {
          setMessages(res.data as ChatMessage[]);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setError("Could not load chat messages.");
          setIsLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [sessionId]);

  const handleSend = async (text: string) => {
    setIsSending(true);
    setError(null);

    const tempUserMsg: ChatMessage = {
      id: generateUuid(),
      role: "USER",
      content: text,
      createdAt: new Date().toISOString(),
      actions: [],
    };

    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const result = await sendChatMessage(sessionId, text, timezone);
      const assistantMsg = result.data.assistantMessage as ChatMessage;
      const actions = result.data.actions as MealDraftActionType[];

      const assistantMsgWithActions: ChatMessage = {
        ...assistantMsg,
        actions: actions.length > 0 ? actions : assistantMsg.actions,
      };

      setMessages((prev) => [...prev, assistantMsgWithActions]);
    } catch {
      setError("Unable to get a response. Please check your network or try again.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="page-container page-container--chat">
      <div className="chat-header card">
        <div className="chat-header__left">
          <Link to="/chat" className="btn btn--outline btn--small">
            ← All Chats
          </Link>
          <div>
            <h1 className="chat-header__title">Nutrition Assistant</h1>
            <span className="chat-header__disclaimer">AI Powered • Not medical advice</span>
          </div>
        </div>
      </div>

      {error && <Alert>{error}</Alert>}

      <div className="chat-main-card card">
        {isLoading ? (
          <LoadingState />
        ) : messages.length === 0 ? (
          <div className="chat-empty-state">
            <div className="chat-empty-icon">🥗</div>
            <h3>Hello! How can I assist with your nutrition today?</h3>
            <p>
              You can ask for meal suggestions, log foods via natural language, or review your calorie targets.
            </p>
          </div>
        ) : (
          <ChatMessageList messages={messages} isTyping={isSending} />
        )}

        <ChatComposer onSend={handleSend} isLoading={isSending} disabled={isLoading} />
      </div>
    </div>
  );
}
