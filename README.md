# 印尼 App 分类打标 Agent

这是一个完全基于大模型的 App 分类打标命令行工具，适合对印尼 Google Play App 描述进行单条或批量分类。工具会把分类体系、风险相关性规则和输出 JSON 结构写入 prompt，并在模型返回后做一次本地标准化校验，保证 `category_code`、`level1/2/3`、`category_path` 和 `risk_relevance` 匹配。

## 文件说明

- `app_classifier_agent.py`：命令行入口。
- `prompts.py`：分类专家 prompt。
- `categories.py`：类别编码、路径、风险等级和标准化逻辑。
- `.env.example`：环境变量示例。
- `examples/input_single.json`：单条输入示例。
- `examples/input_batch.json`：批量输入示例。

## 配置 API Key

PowerShell 临时配置：

```powershell
$env:LLM_API_KEY="你的apikey"
$env:LLM_MODEL="gpt-4o-mini"
$env:LLM_BASE_URL="https://api.openai.com/v1"
```

也可以直接在命令里传：

```powershell
python app_classifier_agent.py --api-key "你的apikey" --input-file examples/input_single.json
```

如果你用的是其他 OpenAI 兼容供应商，把 `LLM_BASE_URL` 改成对应地址即可，例如 `https://xxx/v1`。

## 网页小工具

Streamlit 版本：

```powershell
streamlit run streamlit_app.py
```

这个版本支持本地 RAG 样例库。你可以在「RAG 样例库」页上传已打标样例 JSON/JSONL/CSV/Excel，也可以在打标后把本次结果追加进样例库。默认样例库存储在 `data/label_examples.jsonl`。

待打标文件支持 `json`、`csv`、`xlsx`、`xls`。Excel/CSV 的列名建议包含：

```text
package_name, app_name, description, category, tag
```

如果上传的是 Excel，打标完成后可以下载 `source_with_labels.xlsx`，它会保留源文件原始列，并在最后追加一列 `打标结果`。

原生 Python 版本：

启动本地网页服务：

```powershell
python web_server.py
```

然后在浏览器打开：

```text
http://127.0.0.1:8765
```

网页端支持粘贴单条 App JSON 或批量 JSON 数组，也支持导入 `.json` 文件。API Key 可以填在页面里，也可以提前设置 `LLM_API_KEY` 环境变量后留空。

## 单条分类

```powershell
python app_classifier_agent.py --input-file examples/input_single.json
```

或直接传 JSON：

```powershell
python app_classifier_agent.py --input '{ "package_name": "com.loan.demo", "app_name": "Dana Cepat", "description": "Pinjaman tunai online cepat cair ke rekening bank.", "category": "Finance", "tag": "loan" }'
```

## 批量分类

```powershell
python app_classifier_agent.py --input-file examples/input_batch.json --output-file output.json
```

默认每批请求 20 条，可以调整：

```powershell
python app_classifier_agent.py --input-file apps.json --output-file labels.json --batch-size 10
```

## 输出

输出严格 JSON。单条输入返回 JSON 对象，批量输入返回等长、同顺序 JSON 数组。

## 离线冒烟测试

不调用模型，只检查本地类别标准化逻辑：

```powershell
python smoke_test.py
```

## 常用参数

- `--model`：模型名，默认读取 `LLM_MODEL`，否则使用 `gpt-4o-mini`。
- `--base-url`：接口地址，默认读取 `LLM_BASE_URL`，否则使用 `https://api.openai.com/v1`。
- `--temperature`：默认 `0.0`，分类任务建议保持低温。
- `--timeout`：默认 `120` 秒。
- `--retries`：默认失败重试 2 次。
