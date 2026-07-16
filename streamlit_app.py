"""Streamlit UI for LLM-based Indonesian app classification with local RAG."""

import json
import os
import re
from argparse import Namespace
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from app_classifier_agent import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    ClassificationError,
    classify_batches,
    load_json_value,
)
from rag_store import (
    DEFAULT_STORE,
    append_examples,
    format_examples_for_prompt,
    load_examples,
    replace_examples,
    retrieve_examples,
)


CHECKPOINT_DIR = Path("data") / "checkpoints"

SAMPLE_INPUT = [
    {
        "package_name": "com.example.danacepat",
        "app_name": "Dana Cepat",
        "description": "Pinjaman tunai online cepat cair ke rekening bank. Ajukan kredit hanya dengan KTP dan dapatkan limit pinjaman dalam beberapa menit.",
        "category": "Finance",
        "tag": "loan, credit",
    },
    {
        "package_name": "com.example.shop",
        "app_name": "Belanja Murah",
        "description": "Online shopping marketplace with product search, seller stores, vouchers, secure checkout and delivery tracking.",
        "category": "Shopping",
        "tag": "marketplace, ecommerce",
    },
]


def pretty(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def result_rows(result):
    if isinstance(result, list):
        return result
    if isinstance(result, dict) and result:
        return [result]
    return []


def safe_stem(name):
    stem = Path(name).stem if name else "manual_input"
    stem = re.sub(r"[^0-9A-Za-z._-]+", "_", stem)
    return stem[:80] or "manual_input"


def checkpoint_path_for(uploaded_input):
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    return CHECKPOINT_DIR / f"{safe_stem(getattr(uploaded_input, 'name', 'manual_input'))}_labels.jsonl"


def load_checkpoint(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def append_checkpoint(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for row in result_rows(rows):
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def dataframe_to_records(frame):
    clean = frame.copy().where(pd.notnull(frame), "")
    return clean.to_dict(orient="records")


def uploaded_bytes(uploaded_file):
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.getvalue()
    return uploaded_file.read()


def read_table_file_with_meta(uploaded_file):
    name = uploaded_file.name.lower()
    content = uploaded_bytes(uploaded_file)
    if name.endswith(".jsonl"):
        text = content.decode("utf-8-sig")
        return [json.loads(line) for line in text.splitlines() if line.strip()], None, "jsonl"
    if name.endswith(".json"):
        text = content.decode("utf-8-sig")
        parsed = json.loads(text)
        return (parsed if isinstance(parsed, list) else [parsed]), None, "json"
    if name.endswith(".csv"):
        frame = pd.read_csv(BytesIO(content))
        clean = frame.where(pd.notnull(frame), "")
        return dataframe_to_records(frame), clean, "csv"
    if name.endswith(".xlsx") or name.endswith(".xls"):
        frame = pd.read_excel(BytesIO(content))
        clean = frame.where(pd.notnull(frame), "")
        return dataframe_to_records(frame), clean, "excel"
    raise ValueError("只支持 JSON、JSONL、CSV、XLSX、XLS 文件。")


def read_table_file(uploaded_file):
    records, _frame, _kind = read_table_file_with_meta(uploaded_file)
    return records


def build_source_labeled_frame(source_frame, rows):
    frame = source_frame.copy()
    frame["打标结果"] = [
        row.get("category_path") or row.get("category_code") or "" for row in rows
    ]
    return frame


def excel_bytes(frame, sheet_name="labels"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def sidebar_settings():
    st.sidebar.header("模型配置")
    api_key = st.sidebar.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="可留空，使用本地 .env",
    )
    model = st.sidebar.text_input("Model", value=os.getenv("LLM_MODEL", DEFAULT_MODEL))
    base_url = st.sidebar.text_input("Base URL", value=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL))
    batch_size = st.sidebar.number_input("Batch Size", min_value=1, max_value=100, value=5)
    max_tokens = st.sidebar.number_input("Max Output Tokens", min_value=1024, max_value=32768, value=DEFAULT_MAX_TOKENS)
    top_k = st.sidebar.number_input("RAG Top K", min_value=0, max_value=20, value=5)
    max_records = st.sidebar.number_input("最多打标条数（0=全部）", min_value=0, value=0)
    return api_key, model, base_url, int(batch_size), int(max_tokens), int(top_k), int(max_records)


def classify_payload(payload, api_key, model, base_url, batch_size, max_tokens, rag_context):
    args = Namespace(
        api_key=api_key or None,
        base_url=base_url,
        model=model,
        temperature=0.0,
        batch_size=batch_size,
        timeout=DEFAULT_TIMEOUT,
        retries=4,
        rag_examples=rag_context,
        max_tokens=max_tokens,
    )
    return classify_batches(payload, args)


def render_rag_manager():
    st.subheader("本地 RAG 样例库")
    examples = load_examples(DEFAULT_STORE)
    st.caption(f"当前样例数：{len(examples)}，存储位置：{DEFAULT_STORE}")

    uploaded = st.file_uploader(
        "导入已打标样例",
        type=["json", "jsonl", "csv", "xlsx", "xls"],
        accept_multiple_files=False,
        help="Excel/CSV 的列名建议包含 package_name、app_name、description、category_code、category_path 等字段。",
    )
    mode = st.radio("导入方式", ["追加", "覆盖"], horizontal=True)
    if uploaded and st.button("导入样例"):
        try:
            records = read_table_file(uploaded)
            if mode == "覆盖":
                replace_examples(records, DEFAULT_STORE)
            else:
                append_examples(records, DEFAULT_STORE)
            st.success(f"已导入 {len(records)} 条样例")
            st.rerun()
        except Exception as exc:
            st.error(f"导入失败：{exc}")

    with st.expander("查看样例库", expanded=False):
        if examples:
            st.dataframe(examples[:200], width="stretch")
            st.caption("这里只预览前 200 条，下载文件包含全部样例。")
            st.download_button(
                "下载样例库 JSONL",
                data="\n".join(json.dumps(item, ensure_ascii=False) for item in examples) + "\n",
                file_name="label_examples.jsonl",
                mime="application/json",
            )
        else:
            st.info("还没有样例。你可以上传历史打标结果，或先打标后把结果追加进样例库。")


def render_result_panel():
    st.subheader("结果")
    output_slot = st.empty()
    if "last_result" not in st.session_state:
        output_slot.info("结果会显示在这里。")
        return output_slot

    rows = result_rows(st.session_state.last_result)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("记录数", len(rows))
    c2.metric("High", sum(1 for row in rows if row.get("risk_relevance") == "High"))
    c3.metric("Medium", sum(1 for row in rows if row.get("risk_relevance") == "Medium"))
    c4.metric("Low", sum(1 for row in rows if row.get("risk_relevance") == "Low"))

    if rows:
        st.dataframe(rows[:200], width="stretch")
        if len(rows) > 200:
            st.caption("结果表只预览前 200 条，下载文件包含全部结果。")
    output_slot.json(rows[:20] if isinstance(st.session_state.last_result, list) else st.session_state.last_result)

    st.download_button(
        "下载结果 JSON",
        data=pretty(st.session_state.last_result) + "\n",
        file_name="app_labels.json",
        mime="application/json",
    )
    if rows:
        st.download_button(
            "下载结果 CSV",
            data=pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"),
            file_name="app_labels.csv",
            mime="text/csv",
        )
        st.download_button(
            "下载结果 Excel",
            data=excel_bytes(pd.DataFrame(rows)),
            file_name="app_labels.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        source_frame = st.session_state.get("source_frame")
        source_kind = st.session_state.get("source_kind")
        if source_frame is not None and len(source_frame) == len(rows):
            labeled_source = build_source_labeled_frame(source_frame, rows)
            if source_kind == "excel":
                st.download_button(
                    "下载源 Excel + 打标结果",
                    data=excel_bytes(labeled_source, sheet_name="labels"),
                    file_name="source_with_labels.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            elif source_kind == "csv":
                st.download_button(
                    "下载源 CSV + 打标结果",
                    data=labeled_source.to_csv(index=False).encode("utf-8-sig"),
                    file_name="source_with_labels.csv",
                    mime="text/csv",
                )
    if rows and st.button("把本次结果追加到 RAG 样例库"):
        append_examples(rows, DEFAULT_STORE)
        st.success(f"已追加 {len(rows)} 条结果到样例库")
    return output_slot


def load_input_payload(uploaded_input, manual_text):
    if uploaded_input:
        payload, source_frame, source_kind = read_table_file_with_meta(uploaded_input)
        st.session_state.source_frame = source_frame
        st.session_state.source_kind = source_kind
        return payload, True

    st.session_state.source_frame = None
    st.session_state.source_kind = None
    return load_json_value(manual_text), False


def main():
    st.set_page_config(page_title="印尼 App 分类打标工具", layout="wide")
    st.title("印尼 App 分类打标工具")
    st.caption("基于大模型分类，支持 JSON、CSV、Excel 输入和本地 RAG 样例参考。")

    api_key, model, base_url, batch_size, max_tokens, top_k, max_records = sidebar_settings()

    tabs = st.tabs(["打标", "RAG 样例库"])
    with tabs[0]:
        left, right = st.columns([1, 1])
        with left:
            st.subheader("输入 App 数据")
            uploaded_input = st.file_uploader(
                "导入待打标文件",
                type=["json", "csv", "xlsx", "xls"],
                key="input_file",
                help="Excel/CSV 的列名建议包含 package_name、app_name、description、category、tag。",
            )

            manual_text = ""
            checkpoint_path = checkpoint_path_for(uploaded_input) if uploaded_input else checkpoint_path_for(None)
            if uploaded_input:
                try:
                    payload, source_frame, source_kind = read_table_file_with_meta(uploaded_input)
                    st.session_state.source_frame = source_frame
                    st.session_state.source_kind = source_kind
                    st.session_state.upload_payload = payload
                    st.success(f"已读取 {len(payload)} 条记录。大文件模式不会把全量数据塞进文本框。")
                    st.dataframe(payload[:20], width="stretch")
                    if len(payload) > 20:
                        st.caption("这里只预览前 20 条，打标会使用上传文件的全部记录。")
                    checkpoint_rows = load_checkpoint(checkpoint_path)
                    if checkpoint_rows:
                        st.info(f"检测到断点文件：{checkpoint_path}，已完成 {len(checkpoint_rows)} 条。再次开始会自动续跑。")
                except Exception as exc:
                    st.error(f"文件读取失败：{exc}")
                    st.session_state.upload_payload = None
                    st.session_state.source_frame = None
                    st.session_state.source_kind = None
            else:
                st.session_state.upload_payload = None
                st.session_state.source_frame = None
                st.session_state.source_kind = None
                manual_text = st.text_area(
                    "单条对象或批量数组",
                    value=pretty(SAMPLE_INPUT),
                    height=420,
                )

            reset_checkpoint = st.checkbox("清空断点，从头重新打标", value=False)
            use_rag = st.checkbox("启用本地 RAG 样例参考", value=True)
            classify_clicked = st.button("开始打标", type="primary")

        with right:
            output_slot = render_result_panel()

        if classify_clicked:
            try:
                payload, _from_file = load_input_payload(uploaded_input, manual_text)
                if max_records > 0:
                    payload = payload[:max_records] if isinstance(payload, list) else payload
                    source_frame = st.session_state.get("source_frame")
                    if source_frame is not None:
                        st.session_state.source_frame = source_frame.iloc[:max_records].copy()

                checkpoint_path = checkpoint_path_for(uploaded_input)
                if reset_checkpoint and checkpoint_path.exists():
                    checkpoint_path.unlink()
                checkpoint_rows = load_checkpoint(checkpoint_path) if isinstance(payload, list) else []
                if checkpoint_rows:
                    completed_from_checkpoint = min(len(checkpoint_rows), len(payload))
                    payload_to_label = payload[completed_from_checkpoint:]
                    st.session_state.last_result = checkpoint_rows[:completed_from_checkpoint]
                    st.info(f"从断点续跑：已跳过 {completed_from_checkpoint} 条，剩余 {len(payload_to_label)} 条。")
                else:
                    completed_from_checkpoint = 0
                    payload_to_label = payload
                    if isinstance(payload, list):
                        st.session_state.last_result = []

                examples = load_examples(DEFAULT_STORE)
                rag_query_payload = payload_to_label[:200] if isinstance(payload_to_label, list) and len(payload_to_label) > 200 else payload_to_label
                retrieved = retrieve_examples(rag_query_payload, examples, top_k=top_k) if use_rag and top_k else []
                rag_context = format_examples_for_prompt(retrieved)

                if retrieved:
                    with st.expander("本次检索到的参考样例", expanded=False):
                        st.dataframe(retrieved, width="stretch")

                progress_bar = st.progress(0, text="准备开始打标...")
                progress_status = st.empty()
                progress_preview = st.empty()
                with st.spinner("模型正在打标..."):
                    for progress in classify_payload(
                        payload_to_label, api_key, model, base_url, batch_size, max_tokens, rag_context
                    ):
                        batch_rows = result_rows(progress["batch_result"])
                        if batch_rows and isinstance(payload, list):
                            append_checkpoint(checkpoint_path, batch_rows)
                        completed = completed_from_checkpoint + progress["completed"]
                        total = len(payload) if isinstance(payload, list) else progress["total"]
                        percent = completed / total if total else 1
                        if isinstance(payload, list):
                            st.session_state.last_result = checkpoint_rows[:completed_from_checkpoint] + progress["result"]
                        else:
                            st.session_state.last_result = progress["result"]
                        progress_bar.progress(
                            min(1.0, percent),
                            text=f"打标进度：{completed}/{total}",
                        )
                        progress_status.info(f"已完成 {completed} 条，共 {total} 条。")
                        progress_preview.dataframe(
                            result_rows(progress["result"])[-20:],
                            width="stretch",
                        )
                progress_bar.progress(1.0, text="打标完成")
                st.rerun()
            except (ClassificationError, json.JSONDecodeError, ValueError) as exc:
                output_slot.error(str(exc))

    with tabs[1]:
        render_rag_manager()


if __name__ == "__main__":
    main()
