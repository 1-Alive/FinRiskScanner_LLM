"""Offline smoke test for output normalization."""

import json

from categories import normalize_record


SAMPLE_MODEL_RECORD = {
    "package_name": "will_be_overwritten",
    "app_name": "will_be_overwritten",
    "description_language": "Indonesian",
    "is_description_sufficient": True,
    "main_function_summary": "提供线上现金贷款申请",
    "category_code": "FIN_LOAN_MICRO_CASH",
    "level1": "",
    "level2": "",
    "level3": "",
    "category_path": "",
    "risk_relevance": "",
    "confidence": 0.92,
    "reason": "描述提到现金贷款",
}


if __name__ == "__main__":
    print(json.dumps(normalize_record(SAMPLE_MODEL_RECORD), ensure_ascii=False, indent=2))
