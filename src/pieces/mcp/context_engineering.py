import os
import re
from typing import Any


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "who",
    "with",
}

_APP_SOURCE_KEYWORDS = {
    "chrome": "Google Chrome",
    "cursor": "Cursor",
    "vscode": "Code",
    "vs code": "Code",
    "code": "Code",
    "claude": "Claude",
    "chatgpt": "ChatGPT",
    "warp": "Warp",
    "kitty": "kitty",
    "notion": "Notes",
    "whatsapp": "WhatsApp",
    "mail": "Mail",
    "obsidian": "Obsidian",
}


def _env_csv_list(key: str) -> list[str]:
    value = os.getenv(key, "")
    return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_files(files: list[str]) -> list[str]:
    normalized: list[str] = []
    for file in files:
        if not isinstance(file, str) or not file.strip():
            continue
        path = os.path.abspath(os.path.expanduser(file.strip()))
        if path not in normalized:
            normalized.append(path)
    return normalized


def _infer_topics(question: str, max_topics: int = 5) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_./-]+", question.lower())
    topics: list[str] = []
    for word in words:
        if len(word) < 3 or word in _STOP_WORDS:
            continue
        if word not in topics:
            topics.append(word)
        if len(topics) >= max_topics:
            break
    return topics


def _infer_application_sources(question: str) -> list[str]:
    normalized = question.lower()
    sources: list[str] = []
    for key, source in _APP_SOURCE_KEYWORDS.items():
        if key in normalized and source not in sources:
            sources.append(source)
    if ("http://" in normalized or "https://" in normalized or "browser" in normalized) and "Google Chrome" not in sources:
        sources.append("Google Chrome")
    return sources


def _build_related_questions(question: str) -> list[str]:
    if not question:
        return []
    return [
        f"What files or workstreams are most relevant to: {question}",
        f"What did I recently change related to: {question}",
    ]


def _derive_summary_description(summary: str) -> str:
    cleaned = " ".join(summary.strip().split())
    if not cleaned:
        return "Project memory"
    sentence = cleaned.split(".")[0].strip()
    if sentence:
        return sentence[:120]
    return cleaned[:120]


def optimize_tool_arguments(tool_name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    args: dict[str, Any] = dict(arguments or {})
    connected_client = os.getenv("PIECES_CONNECTED_CLIENT", "pieces-cli")

    if tool_name == "ask_pieces_ltm":
        question = str(args.get("question", "")).strip()
        if question:
            args["question"] = question
        if not args.get("topics") and question:
            args["topics"] = _infer_topics(question)
        if not args.get("open_files"):
            args["open_files"] = _normalize_files(_env_csv_list("PIECES_OPEN_FILES"))
        if not args.get("application_sources") and question:
            args["application_sources"] = _infer_application_sources(question)
        if not args.get("related_questions") and question:
            args["related_questions"] = _build_related_questions(question)
        args.setdefault("chat_llm", os.getenv("PIECES_CHAT_LLM", "unknown"))
        args.setdefault("connected_client", connected_client)

    if tool_name == "create_pieces_memory":
        args.setdefault("project", os.path.abspath(os.getcwd()))
        files = args.get("files", [])
        if isinstance(files, list):
            args["files"] = _normalize_files(files)
        if not args.get("summary_description") and args.get("summary"):
            args["summary_description"] = _derive_summary_description(str(args["summary"]))
        args.setdefault("connected_client", connected_client)

    return args
