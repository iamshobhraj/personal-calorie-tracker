import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createChatSession, listChatSessions } from "../features/chat/api";
import type { ChatSession } from "../api/contracts/chat";
export function ChatPage(): React.JSX.Element { const [sessions, setSessions] = useState<ChatSession[]>([]); const navigate = useNavigate(); useEffect(() => { void listChatSessions().then(value => setSessions(value.data)).catch(() => setSessions([])); }, []); async function start(): Promise<void> { const session = await createChatSession(); navigate(`/chat/${session.data.id}`); } return <section><h1>Nutrition Assistant <small>Beta</small></h1><p>This assistant is not medical advice. Meal suggestions remain drafts until you confirm them.</p><button onClick={() => void start()}>New chat</button><ul>{sessions.map(item => <li key={item.id}><Link to={`/chat/${item.id}`}>{item.title ?? "Nutrition chat"}</Link></li>)}</ul></section>; }
