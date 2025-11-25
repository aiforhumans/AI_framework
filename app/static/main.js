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

  initTabs();
  initToolsUI();
});


function initTabs() {
  const buttons = document.querySelectorAll(".tab-button");
  const panels = document.querySelectorAll(".tab-panel");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");

      buttons.forEach((b) => b.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const panel = document.getElementById(target);
      if (panel) {
        panel.classList.add("active");
      }
    });
  });
}


async function fetchTools() {
  const res = await fetch("/api/tools");
  if (!res.ok) {
    throw new Error(`Failed to fetch tools: ${res.status}`);
  }
  const data = await res.json();
  return data.tools || [];
}

function renderToolsTable(tools) {
  const tbody = document.querySelector("#tools-table tbody");
  tbody.innerHTML = "";

  tools.forEach((tool) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${tool.id}</td>
      <td>${tool.name}</td>
      <td>${tool.enabled ? "Yes" : "No"}</td>
      <td>
        <button type="button" data-action="edit" data-id="${tool.id}">Edit</button>
        <button type="button" data-action="toggle" data-id="${tool.id}">${tool.enabled ? "Disable" : "Enable"}</button>
        <button type="button" data-action="delete" data-id="${tool.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onToolsTableAction);
  });
}


async function onToolsTableAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.getAttribute("data-id"));
  const action = btn.getAttribute("data-action");

  if (action === "edit") {
    await populateToolForm(id);
  } else if (action === "toggle") {
    await toggleTool(id);
  } else if (action === "delete") {
    const confirmed = window.confirm("Delete this tool?");
    if (confirmed) {
      await deleteTool(id);
    }
  }
}


async function populateToolForm(id) {
  const tools = await fetchTools();
  const tool = tools.find((t) => t.id === id);
  if (!tool) return;

  document.getElementById("tool-id").value = tool.id;
  document.getElementById("tool-name").value = tool.name || "";
  document.getElementById("tool-description").value = tool.description || "";
  document.getElementById("tool-endpoint").value = tool.endpoint || "";
  document.getElementById("tool-models").value = (tool.models || []).join(", ");
  document.getElementById("tool-agents").value = (tool.agents || []).join(", ");
  document.getElementById("tool-input-schema").value = tool.input_schema
    ? JSON.stringify(tool.input_schema, null, 2)
    : "";
  document.getElementById("tool-enabled").checked = !!tool.enabled;
}


async function toggleTool(id) {
  await fetch(`/api/tools/${id}/toggle`, { method: "POST" });
  await refreshToolsUI();
}


async function deleteTool(id) {
  await fetch(`/api/tools/${id}`, { method: "DELETE" });
  await refreshToolsUI();
}


async function submitToolForm(event) {
  event.preventDefault();
  const messageEl = document.getElementById("tool-form-message");
  messageEl.textContent = "";

  const id = document.getElementById("tool-id").value;
  const name = document.getElementById("tool-name").value.trim();
  const description = document.getElementById("tool-description").value.trim();
  const endpoint = document.getElementById("tool-endpoint").value.trim();
  const modelsStr = document.getElementById("tool-models").value.trim();
  const agentsStr = document.getElementById("tool-agents").value.trim();
  const inputSchemaStr = document.getElementById("tool-input-schema").value.trim();
  const enabled = document.getElementById("tool-enabled").checked;

  let inputSchema = {};
  if (inputSchemaStr) {
    try {
      inputSchema = JSON.parse(inputSchemaStr);
    } catch (err) {
      messageEl.textContent = "Invalid JSON in input schema";
      return;
    }
  }

  const models = modelsStr ? modelsStr.split(",").map((s) => s.trim()).filter(Boolean) : [];
  const agents = agentsStr ? agentsStr.split(",").map((s) => s.trim()).filter(Boolean) : [];

  const payload = {
    name,
    description,
    endpoint,
    input_schema: inputSchema,
    enabled,
    models,
    agents,
  };

  const isUpdate = !!id;
  const url = isUpdate ? `/api/tools/${id}` : "/api/tools";
  const method = isUpdate ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    messageEl.textContent = `Save failed: ${res.status}`;
    return;
  }

  messageEl.textContent = "Saved";
  await refreshToolsUI();
}


function resetToolForm() {
  document.getElementById("tool-id").value = "";
  document.getElementById("tool-name").value = "";
  document.getElementById("tool-description").value = "";
  document.getElementById("tool-endpoint").value = "";
  document.getElementById("tool-models").value = "";
  document.getElementById("tool-agents").value = "";
  document.getElementById("tool-input-schema").value = "";
  document.getElementById("tool-enabled").checked = true;
  document.getElementById("tool-form-message").textContent = "";
}


async function refreshToolsUI() {
  const tools = await fetchTools();
  renderToolsTable(tools);
}


function initToolsUI() {
  const form = document.getElementById("tool-form");
  const resetBtn = document.getElementById("tool-reset-btn");
  if (!form) return;

  form.addEventListener("submit", submitToolForm);
  resetBtn.addEventListener("click", resetToolForm);

  refreshToolsUI().catch((err) => {
    const messageEl = document.getElementById("tool-form-message");
    if (messageEl) {
      messageEl.textContent = `Failed to load tools: ${err}`;
    }
  });
}
