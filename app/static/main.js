async function runPrompt() {
  const agentSelect = document.getElementById("agent-select");
  const modelSelect = document.getElementById("model-select");
  const promptEl = document.getElementById("prompt");
  const maxTokensEl = document.getElementById("max-tokens");
  const temperatureEl = document.getElementById("temperature");
  const responseOutput = document.getElementById("response-output");
  const metaEl = document.getElementById("meta");

  const payload = {
    agent_id: agentSelect.value || null,
    model_name: modelSelect.value || null,
    prompt: promptEl.value,
    max_tokens: maxTokensEl.value ? Number(maxTokensEl.value) : null,
    temperature: temperatureEl.value ? Number(temperatureEl.value) : null,
  };

  responseOutput.textContent = "Running...";
  metaEl.textContent = "";

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      responseOutput.textContent = `Error: ${res.status} ${text}`;
      return;
    }

    const data = await res.json();
    responseOutput.textContent = data.response;
    const agentLabel = data.agent_name ? `Agent: ${data.agent_name} | ` : "";
    metaEl.textContent = `${agentLabel}Model: ${data.model_name} | Latency: ${data.latency_ms.toFixed(1)} ms`;
  } catch (err) {
    responseOutput.textContent = `Request failed: ${err}`;
  }
}

function syncAgentInstructions() {
  const agentSelect = document.getElementById("agent-select");
  const instructionsEl = document.getElementById("agent-instructions");
  const selected = agentSelect.selectedOptions[0];
  const instructions = selected ? selected.getAttribute("data-instructions") : "";
  instructionsEl.value = instructions || "";
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("run-btn");
  btn.addEventListener("click", runPrompt);

  const agentSelect = document.getElementById("agent-select");
  // Inject instructions via data attributes rendered on options
  syncAgentInstructions();
  agentSelect.addEventListener("change", syncAgentInstructions);
});
