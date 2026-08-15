from src.modules.chat.application.tools import ALLOWED_CHAT_TOOLS


def is_allowed_tool(name: str) -> bool:
    return name in ALLOWED_CHAT_TOOLS
