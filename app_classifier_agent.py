"""CLI agent for LLM-based Indonesian app classification."""

import argparse
import http.client
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request

from categories import normalize_record
from prompts import RAG_CONTEXT_TEMPLATE, SYSTEM_PROMPT, USER_PROMPT


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_TOKENS = 8192
TRANSIENT_ERRORS = (
    urllib.error.URLError,
    urllib.error.HTTPError,
    http.client.RemoteDisconnected,
    http.client.HTTPException,
    ConnectionResetError,
    TimeoutError,
    socket.timeout,
)
MODEL_CALL_ERRORS = TRANSIENT_ERRORS + (KeyError, json.JSONDecodeError)


def load_env_file(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


class ClassificationError(RuntimeError):
    pass


def load_json_value(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ClassificationError(f"输入不是合法 JSON: {exc}") from exc


def load_input(args):
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as file:
            return load_json_value(file.read())
    if args.input:
        return load_json_value(args.input)
    raw = sys.stdin.read().strip()
    if raw:
        return load_json_value(raw)
    raise ClassificationError("请通过 --input、--input-file 或 stdin 提供 App JSON。")


def split_batches(payload, batch_size):
    if isinstance(payload, list):
        for start in range(0, len(payload), batch_size):
            yield payload[start : start + batch_size], True
    elif isinstance(payload, dict):
        yield payload, False
    else:
        raise ClassificationError("输入必须是 JSON 对象或 JSON 数组。")


def payload_size(payload):
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        return 1
    raise ClassificationError("输入必须是 JSON 对象或 JSON 数组。")


def build_rag_context(rag_examples):
    if not rag_examples:
        return ""
    return RAG_CONTEXT_TEMPLATE.format(examples=rag_examples)


def extract_chat_content(data):
    if not isinstance(data, dict):
        raise ClassificationError(f"模型返回格式异常: {data!r}")

    if data.get("error"):
        raise ClassificationError(f"模型接口返回错误: {data['error']}")

    choices = data.get("choices")
    if not choices:
        raise ClassificationError(f"模型返回缺少 choices: {str(data)[:500]}")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not content:
        finish_reason = choices[0].get("finish_reason") if isinstance(choices[0], dict) else None
        raise ClassificationError(f"模型返回内容为空，finish_reason={finish_reason}, raw={str(data)[:500]}")

    return content


def chat_completion(
    payload,
    api_key,
    base_url,
    model,
    temperature,
    timeout,
    retries,
    rag_examples="",
    max_tokens=DEFAULT_MAX_TOKENS,
):
    url = base_url.rstrip("/") + "/chat/completions"
    request_body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(
                    rag_context=build_rag_context(rag_examples),
                    payload=json.dumps(payload, ensure_ascii=False, indent=2)
                ),
            },
        ],
    }

    last_error = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return extract_chat_content(data)
        except (MODEL_CALL_ERRORS, ClassificationError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(30, 2 ** attempt))
                continue
            raise ClassificationError(f"模型调用失败: {last_error}") from exc


def parse_model_json(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ClassificationError(f"模型返回不是合法 JSON: {content[:500]}") from exc


def ensure_output_shape(input_payload, output_payload, was_batch):
    if was_batch:
        if isinstance(output_payload, dict) and "items" in output_payload:
            output_payload = output_payload["items"]
        if not isinstance(output_payload, list):
            raise ClassificationError("批量输入时模型必须返回 JSON 数组。")
        if len(output_payload) != len(input_payload):
            raise ClassificationError(
                f"批量输出数量不一致: 输入 {len(input_payload)} 条，输出 {len(output_payload)} 条。"
            )
        return output_payload

    if isinstance(output_payload, dict) and "items" in output_payload:
        items = output_payload["items"]
        if isinstance(items, list) and len(items) == 1:
            output_payload = items[0]
    if not isinstance(output_payload, dict):
        raise ClassificationError("单条输入时模型必须返回 JSON 对象。")
    return output_payload


def fill_identity(input_payload, output_payload, was_batch):
    if was_batch:
        normalized = []
        for app, record in zip(input_payload, output_payload):
            if not isinstance(record, dict):
                raise ClassificationError("批量输出中的每条记录都必须是 JSON 对象。")
            record["package_name"] = app.get("package_name", "")
            record["app_name"] = app.get("app_name", "")
            normalized.append(normalize_record(record))
        return normalized

    output_payload["package_name"] = input_payload.get("package_name", "")
    output_payload["app_name"] = input_payload.get("app_name", "")
    return normalize_record(output_payload)


def classify_one_batch(batch_payload, was_batch, args, api_key):
    content = chat_completion(
        batch_payload,
        api_key=api_key,
        base_url=args.base_url,
        model=args.model,
        temperature=args.temperature,
        timeout=args.timeout,
        retries=args.retries,
        rag_examples=getattr(args, "rag_examples", ""),
        max_tokens=getattr(args, "max_tokens", DEFAULT_MAX_TOKENS),
    )
    parsed = parse_model_json(content)
    shaped = ensure_output_shape(batch_payload, parsed, was_batch)
    return fill_identity(batch_payload, shaped, was_batch)


def classify_batch_adaptive(batch_payload, was_batch, args, api_key):
    try:
        yield classify_one_batch(batch_payload, was_batch, args, api_key)
    except ClassificationError:
        if not was_batch or not isinstance(batch_payload, list) or len(batch_payload) <= 1:
            raise
        midpoint = len(batch_payload) // 2
        left = batch_payload[:midpoint]
        right = batch_payload[midpoint:]
        yield from classify_batch_adaptive(left, True, args, api_key)
        yield from classify_batch_adaptive(right, True, args, api_key)


def classify(payload, args):
    final_result = None
    for progress in classify_batches(payload, args):
        final_result = progress["result"]
    if final_result is None and isinstance(payload, list):
        return []
    return final_result


def classify_batches(payload, args):
    api_key = args.api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ClassificationError("缺少 API Key。请设置 LLM_API_KEY/OPENAI_API_KEY 或使用 --api-key。")

    results = []
    single_result = None
    total = payload_size(payload)
    completed = 0
    if total == 0:
        yield {
            "completed": 0,
            "total": 0,
            "result": [],
            "batch_result": [],
        }
        return
    for batch_payload, was_batch in split_batches(payload, args.batch_size):
        for normalized in classify_batch_adaptive(batch_payload, was_batch, args, api_key):
            normalized_count = len(normalized) if isinstance(normalized, list) else 1
            if was_batch:
                results.extend(normalized)
                completed += normalized_count
                current_result = results
            else:
                single_result = normalized
                completed = 1
                current_result = single_result

            yield {
                "completed": completed,
                "total": total,
                "result": current_result,
                "batch_result": normalized,
            }


def write_output(result, output_file):
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text + "\n")
    else:
        print(text)


def build_parser():
    parser = argparse.ArgumentParser(
        description="LLM-based Indonesian Google Play app classification agent."
    )
    parser.add_argument("--input", help="单条 App JSON 或批量 App JSON 数组。")
    parser.add_argument("--input-file", help="输入 JSON 文件路径。")
    parser.add_argument("--output-file", help="输出 JSON 文件路径。")
    parser.add_argument("--api-key", help="大模型 API Key；也可用 LLM_API_KEY 或 OPENAI_API_KEY。")
    parser.add_argument("--base-url", default=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = load_input(args)
        result = classify(payload, args)
        write_output(result, args.output_file)
    except ClassificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
