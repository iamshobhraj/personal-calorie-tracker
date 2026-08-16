import type { ChatMessage } from "../api/contracts/chat";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { listChatMessages, sendChatMessage } from "../features/chat/api";

export function ChatSessionPage(): React.JSX.Element {
  const { sessionId = "" } = useParams();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    void listChatMessages(sessionId).then((value) => setMessages(value.data as ChatMessage[])).catch(() => setMessages([]));
  }, [sessionId]);

  async function submit(): Promise<void> {
    const content = message.trim();
    if (!content) return;
    const result = await sendChatMessage(sessionId, content, Intl.DateTimeFormat().resolvedOptions().timeZone);
    setMessages((items) => [
      ...items,
      { id: result.data.userMessageId, role: "USER", content, createdAt: new Date().toISOString(), actions: [] },
      result.data.assistantMessage as ChatMessage,
    ]);
    setMessage("");
  }

  return <section><h1>Nutrition Assistant</h1><p>This assistant is not medical advice.</p><ol>{messages.filter((item) => item.role !== "TOOL").map((item) => <li key={item.id}><strong>{item.role}</strong>: {item.content}</li>)}</ol><textarea maxLength={2000} value={message} onChange={(event) => setMessage(event.target.value)} /><button onClick={() => void submit()}>Send</button></section>;
}
