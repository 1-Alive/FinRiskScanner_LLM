const sample = [
  {
    package_name: "com.example.danacepat",
    app_name: "Dana Cepat",
    description:
      "Pinjaman tunai online cepat cair ke rekening bank. Ajukan kredit hanya dengan KTP dan dapatkan limit pinjaman dalam beberapa menit.",
    category: "Finance",
    tag: "loan, credit",
  },
  {
    package_name: "com.example.shop",
    app_name: "Belanja Murah",
    description:
      "Online shopping marketplace with product search, seller stores, vouchers, secure checkout and delivery tracking.",
    category: "Shopping",
    tag: "marketplace, ecommerce",
  },
];

const els = {
  apiKey: document.querySelector("#apiKey"),
  model: document.querySelector("#model"),
  baseUrl: document.querySelector("#baseUrl"),
  batchSize: document.querySelector("#batchSize"),
  inputJson: document.querySelector("#inputJson"),
  outputJson: document.querySelector("#outputJson"),
  status: document.querySelector("#status"),
  summary: document.querySelector("#summary"),
  classifyBtn: document.querySelector("#classifyBtn"),
  sampleBtn: document.querySelector("#sampleBtn"),
  formatBtn: document.querySelector("#formatBtn"),
  clearBtn: document.querySelector("#clearBtn"),
  copyBtn: document.querySelector("#copyBtn"),
  downloadBtn: document.querySelector("#downloadBtn"),
  fileInput: document.querySelector("#fileInput"),
};

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function setStatus(text, mode = "") {
  els.status.textContent = text;
  els.status.className = `status ${mode}`.trim();
}

function parseInput() {
  return JSON.parse(els.inputJson.value);
}

function updateSummary(result) {
  const rows = Array.isArray(result) ? result : result && result.package_name ? [result] : [];
  const counts = { High: 0, Medium: 0, Low: 0 };
  rows.forEach((row) => {
    if (counts[row.risk_relevance] !== undefined) {
      counts[row.risk_relevance] += 1;
    }
  });
  els.summary.innerHTML = `
    <span>记录数：${rows.length}</span>
    <span>High：${counts.High}</span>
    <span>Medium：${counts.Medium}</span>
    <span>Low：${counts.Low}</span>
  `;
}

function setOutput(value) {
  els.outputJson.textContent = typeof value === "string" ? value : pretty(value);
  if (typeof value !== "string") {
    updateSummary(value);
  }
}

async function classify() {
  let parsed;
  try {
    parsed = parseInput();
    els.inputJson.value = pretty(parsed);
  } catch (error) {
    setStatus("JSON 错误", "error");
    setOutput(`输入不是合法 JSON：${error.message}`);
    return;
  }

  els.classifyBtn.disabled = true;
  setStatus("打标中", "loading");
  setOutput("模型正在理解 description 并分类...");

  try {
    const response = await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        api_key: els.apiKey.value.trim(),
        model: els.model.value.trim(),
        base_url: els.baseUrl.value.trim(),
        batch_size: Number(els.batchSize.value || 20),
        input_json: pretty(parsed),
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "请求失败");
    }
    setOutput(data.result);
    setStatus("完成");
  } catch (error) {
    setStatus("失败", "error");
    setOutput(`打标失败：${error.message}`);
  } finally {
    els.classifyBtn.disabled = false;
  }
}

els.sampleBtn.addEventListener("click", () => {
  els.inputJson.value = pretty(sample);
  setStatus("示例已填入");
});

els.formatBtn.addEventListener("click", () => {
  try {
    els.inputJson.value = pretty(parseInput());
    setStatus("已格式化");
  } catch (error) {
    setStatus("JSON 错误", "error");
  }
});

els.clearBtn.addEventListener("click", () => {
  els.inputJson.value = "";
  setOutput({});
  updateSummary({});
  setStatus("已清空");
});

els.copyBtn.addEventListener("click", async () => {
  await navigator.clipboard.writeText(els.outputJson.textContent);
  setStatus("结果已复制");
});

els.downloadBtn.addEventListener("click", () => {
  const blob = new Blob([els.outputJson.textContent + "\n"], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "app_labels.json";
  link.click();
  URL.revokeObjectURL(link.href);
  setStatus("结果已下载");
});

els.fileInput.addEventListener("change", async () => {
  const file = els.fileInput.files[0];
  if (!file) {
    return;
  }
  els.inputJson.value = await file.text();
  try {
    els.inputJson.value = pretty(parseInput());
    setStatus("文件已导入");
  } catch (error) {
    setStatus("JSON 错误", "error");
  }
  els.fileInput.value = "";
});

els.classifyBtn.addEventListener("click", classify);
els.inputJson.value = pretty(sample);
