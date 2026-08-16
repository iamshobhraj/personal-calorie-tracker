import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../api/contracts/chat";
import { MealDraftAction } from "./MealDraftAction";

export function ChatMessageList({
  messages,
  isTyping = false,
}: {
  messages: ChatMessage[];
  isTyping?: boolean;
}): React.JSX.Element {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const visibleMessages = messages.filter((m) => m.role !== "TOOL");

  return (
    <div className="chat-messages-container">
      {visibleMessages.map((msg) => {
        const isUser = msg.role === "USER";
        return (
          <div
            key={msg.id}
            className={`chat-message-row ${isUser ? "chat-message-row--user" : "chat-message-row--assistant"}`}
          >
            {!isUser && <div className="chat-avatar">🤖</div>}
            <div className={`chat-bubble ${isUser ? "chat-bubble--user" : "chat-bubble--assistant"}`}>
              <div className="chat-bubble__content">{msg.content}</div>
              <div className="chat-bubble__time">
                {new Date(msg.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </div>

              {msg.actions.length > 0 && (
                <div className="chat-bubble__actions">
                  {msg.actions.map((action, idx) => (
                    <MealDraftAction key={idx} action={action} />
                  ))}
                </div>
              )}
            </div>
            {isUser && <div className="chat-avatar chat-avatar--user">👤</div>}
          </div>
        );
      })}

      {isTyping && (
        <div className="chat-message-row chat-message-row--assistant">
          <div className="chat-avatar">🤖</div>
          <div className="chat-bubble chat-bubble--assistant chat-bubble--typing">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
