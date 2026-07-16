"""Small local RAG store for labeled app examples."""

import json
import math
import re
from collections import Counter
from pathlib import Path


DEFAULT_STORE = Path("data") / "label_examples.jsonl"
TOKEN_RE = re.compile(r"[\w]+", re.UNICODE)


def app_text(record):
    fields = [
        record.get("app_name", ""),
        record.get("package_name", ""),
        record.get("description", ""),
        record.get("category", ""),
        record.get("tag", ""),
        record.get("category_path", ""),
        record.get("main_function_summary", ""),
    ]
    return " ".join(str(value) for value in fields if value)


def tokenize(text):
    return [token.lower() for token in TOKEN_RE.findall(text or "") if len(token) > 1]


def load_examples(path=DEFAULT_STORE):
    path = Path(path)
    if not path.exists():
        return []
    examples = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                examples.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return examples


def append_examples(records, path=DEFAULT_STORE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(records, dict):
        records = [records]
    with path.open("a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def replace_examples(records, path=DEFAULT_STORE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def cosine(left, right):
    if not left or not right:
        return 0.0
    overlap = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in overlap)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def retrieve_examples(query_records, examples, top_k=5):
    if isinstance(query_records, dict):
        query_records = [query_records]
    query_counter = Counter()
    for record in query_records:
        query_counter.update(tokenize(app_text(record)))

    scored = []
    for example in examples:
        score = cosine(query_counter, Counter(tokenize(app_text(example))))
        if score > 0:
            scored.append((score, example))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [{"score": round(score, 4), **example} for score, example in scored[:top_k]]


def format_examples_for_prompt(examples):
    lines = []
    for index, example in enumerate(examples, 1):
        compact = {
            "app_name": example.get("app_name", ""),
            "package_name": example.get("package_name", ""),
            "description": example.get("description", ""),
            "category_code": example.get("category_code", ""),
            "category_path": example.get("category_path", ""),
            "risk_relevance": example.get("risk_relevance", ""),
            "main_function_summary": example.get("main_function_summary", ""),
            "reason": example.get("reason", ""),
        }
        lines.append(f"样例 {index}: {json.dumps(compact, ensure_ascii=False)}")
    return "\n".join(lines)
