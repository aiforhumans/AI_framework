// ========== Interactive Playground Chat ==========

let chatHistory = [];
let attachments = [];
let isGenerating = false;

function initPlaygroundChat() {
  const runBtn = document.getElementById("run-btn");
  const promptEl = document.getElementById("prompt");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const attachBtn = document.getElementById("attach-btn");
  const fileInput = document.getElementById("file-input");
  const agentSelect = document.getElementById("agent-select");
  const systemPromptEl = document.getElementById("agent-instructions");
  
  const improveSystemBtn = document.getElementById("improve-system-btn");
  const improvePromptBtn = document.getElementById("improve-prompt-btn");
  const promptGeneratorModal = document.getElementById("prompt-generator-modal");
  const promptGeneratorClose = document.getElementById("prompt-generator-close");
  const promptGeneratorRun = document.getElementById("prompt-generator-run");
  const promptGeneratorUseSystem = document.getElementById("prompt-generator-use-system");
  const promptGeneratorUseMessage = document.getElementById("prompt-generator-use-message");
  const promptGeneratorCopy = document.getElementById("prompt-generator-copy");

  if (!runBtn) return;

  runBtn.addEventListener("click", sendMessage);
  clearChatBtn.addEventListener("click", clearChat);
  attachBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileSelect);
  
  // Auto-resize prompt textarea
  promptEl.addEventListener("input", autoResizeTextarea);
  promptEl.addEventListener("keydown", handlePromptKeydown);
  
  // Character counts
  promptEl.addEventListener("input", updatePromptCharCount);
  systemPromptEl.addEventListener("input", updateSystemCharCount);
  
  // Agent change syncs instructions
  agentSelect.addEventListener("change", syncAgentInstructions);
  syncAgentInstructions();
  
  // Prompt Generator
  improveSystemBtn.addEventListener("click", () => openPromptGenerator("system"));
  improvePromptBtn.addEventListener("click", () => openPromptGenerator("message"));
  promptGeneratorClose.addEventListener("click", closePromptGenerator);
  promptGeneratorRun.addEventListener("click", runPromptGenerator);
  promptGeneratorUseSystem.addEventListener("click", () => useGeneratedPrompt("system"));
  promptGeneratorUseMessage.addEventListener("click", () => useGeneratedPrompt("message"));
  promptGeneratorCopy.addEventListener("click", copyGeneratedPrompt);
  
  // Click outside modal to close
  promptGeneratorModal.addEventListener("click", (e) => {
    if (e.target === promptGeneratorModal) closePromptGenerator();
  });
  
  updateSystemCharCount();
  updatePromptCharCount();
}

function autoResizeTextarea(e) {
  const el = e.target;
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 150) + "px";
}

function handlePromptKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!isGenerating) sendMessage();
  }
}

function updatePromptCharCount() {
  const el = document.getElementById("prompt");
  const countEl = document.getElementById("prompt-char-count");
  if (el && countEl) {
    countEl.textContent = `${el.value.length} chars`;
  }
}

function updateSystemCharCount() {
  const el = document.getElementById("agent-instructions");
  const countEl = document.getElementById("system-char-count");
  if (el && countEl) {
    countEl.textContent = el.value.length;
  }
}

function syncAgentInstructions() {
  const agentSelect = document.getElementById("agent-select");
  const instructionsEl = document.getElementById("agent-instructions");
  const selected = agentSelect.selectedOptions[0];
  const instructions = selected ? selected.getAttribute("data-instructions") : "";
  instructionsEl.value = instructions || "";
  updateSystemCharCount();
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  files.forEach((file) => {
    const reader = new FileReader();
    reader.onload = (ev) => {
      attachments.push({
        name: file.name,
        type: file.type,
        data: ev.target.result,
      });
      renderAttachments();
    };
    if (file.type.startsWith("image/")) {
      reader.readAsDataURL(file);
    } else {
      reader.readAsText(file);
    }
  });
  e.target.value = "";
}

function renderAttachments() {
  const bar = document.getElementById("attachments-bar");
  const list = document.getElementById("attachments-list");
  
  if (attachments.length === 0) {
    bar.style.display = "none";
    return;
  }
  
  bar.style.display = "block";
  list.innerHTML = "";
  
  attachments.forEach((att, idx) => {
    const div = document.createElement("div");
    div.className = "attachment-preview";
    
    if (att.type.startsWith("image/")) {
      div.innerHTML = `<img src="${att.data}" alt="${att.name}" />`;
    } else {
      div.innerHTML = `<span>📄 ${att.name}</span>`;
    }
    
    const removeBtn = document.createElement("button");
    removeBtn.className = "attachment-remove";
    removeBtn.textContent = "×";
    removeBtn.onclick = () => {
      attachments.splice(idx, 1);
      renderAttachments();
    };
    div.appendChild(removeBtn);
    list.appendChild(div);
  });
}

function clearChat() {
  chatHistory = [];
  attachments = [];
  renderChatMessages();
  renderAttachments();
}

function renderChatMessages() {
  const container = document.getElementById("chat-messages");
  
  if (chatHistory.length === 0) {
    container.innerHTML = `
      <div class="chat-welcome">
        <div class="welcome-icon">💬</div>
        <h3>Start a Conversation</h3>
        <p>Type a message below to begin testing. Use the ✨ Improve button to enhance your prompts with AI.</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = "";
  
  chatHistory.forEach((msg, idx) => {
    const div = document.createElement("div");
    div.className = `chat-message ${msg.role}`;
    div.id = `message-${idx}`;
    
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = msg.role === "user" ? "👤" : "🤖";
    
    const content = document.createElement("div");
    content.className = "message-content";
    
    const text = document.createElement("div");
    text.className = "message-text";
    text.textContent = msg.content;
    content.appendChild(text);
    
    // Render attachments for user messages
    if (msg.attachments && msg.attachments.length > 0) {
      const attDiv = document.createElement("div");
      attDiv.className = "message-attachments";
      msg.attachments.forEach((att) => {
        if (att.type.startsWith("image/")) {
          const img = document.createElement("img");
          img.className = "message-attachment";
          img.src = att.data;
          img.alt = att.name;
          attDiv.appendChild(img);
        }
      });
      content.appendChild(attDiv);
    }
    
    // Meta info for assistant messages
    if (msg.role === "assistant" && msg.meta) {
      const meta = document.createElement("div");
      meta.className = "message-meta";
      meta.textContent = `${msg.meta.model} • ${msg.meta.latency_ms}ms`;
      content.appendChild(meta);
    }
    
    div.appendChild(avatar);
    div.appendChild(content);
    container.appendChild(div);
  });
  
  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  const promptEl = document.getElementById("prompt");
  const runBtn = document.getElementById("run-btn");
  const userMessage = promptEl.value.trim();
  
  if (!userMessage && attachments.length === 0) return;
  if (isGenerating) return;
  
  isGenerating = true;
  runBtn.disabled = true;
  
  // Add user message
  const userEntry = {
    role: "user",
    content: userMessage,
    attachments: [...attachments],
  };
  chatHistory.push(userEntry);
  
  // Clear input
  promptEl.value = "";
  promptEl.style.height = "auto";
  attachments = [];
  renderAttachments();
  updatePromptCharCount();
  renderChatMessages();
  
  // Add placeholder for assistant response
  const assistantEntry = {
    role: "assistant",
    content: "",
    streaming: true,
  };
  chatHistory.push(assistantEntry);
  renderChatMessages();
  
  // Mark as streaming
  const msgIdx = chatHistory.length - 1;
  const msgEl = document.getElementById(`message-${msgIdx}`);
  if (msgEl) msgEl.querySelector(".message-content").classList.add("message-streaming");
  
  try {
    const agentSelect = document.getElementById("agent-select");
    const modelSelect = document.getElementById("model-select");
    const maxTokensEl = document.getElementById("max-tokens");
    const temperatureEl = document.getElementById("temperature");
    const systemPromptEl = document.getElementById("agent-instructions");
    const chatModeEl = document.getElementById("chat-mode");
    const streamModeEl = document.getElementById("stream-mode");
    
    // Build messages for chat mode
    let messages = [];
    const systemPrompt = systemPromptEl.value.trim();
    if (systemPrompt) {
      messages.push({ role: "system", content: systemPrompt });
    }
    
    if (chatModeEl.checked) {
      // Include full conversation history
      chatHistory.slice(0, -1).forEach((msg) => {
        if (msg.role === "user" || msg.role === "assistant") {
          messages.push({ role: msg.role, content: msg.content });
        }
      });
    } else {
      // Single turn - just the last user message
      messages.push({ role: "user", content: userMessage });
    }
    
    const payload = {
      agent_id: agentSelect.value || null,
      model_name: modelSelect.value || null,
      messages: messages,
      max_tokens: maxTokensEl.value ? Number(maxTokensEl.value) : null,
      temperature: temperatureEl.value ? Number(temperatureEl.value) : null,
      stream: streamModeEl.checked,
    };
    
    // Add image attachments if present
    if (userEntry.attachments.some((a) => a.type.startsWith("image/"))) {
      payload.images = userEntry.attachments
        .filter((a) => a.type.startsWith("image/"))
        .map((a) => a.data);
    }
    
    if (streamModeEl.checked) {
      // Streaming response
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let fullContent = "";
      let meta = null;
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.content) {
                fullContent += data.content;
                chatHistory[msgIdx].content = fullContent;
                renderChatMessages();
              }
              if (data.done) {
                meta = { model: data.model_name, latency_ms: data.latency_ms };
              }
            } catch (e) {
              console.error("SSE parse error:", e);
            }
          }
        }
      }
      
      chatHistory[msgIdx].content = fullContent;
      chatHistory[msgIdx].streaming = false;
      chatHistory[msgIdx].meta = meta;
    } else {
      // Non-streaming response
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      chatHistory[msgIdx].content = data.response;
      chatHistory[msgIdx].streaming = false;
      chatHistory[msgIdx].meta = {
        model: data.model_name,
        latency_ms: data.latency_ms,
      };
    }
  } catch (err) {
    chatHistory[msgIdx].content = `Error: ${err.message}`;
    chatHistory[msgIdx].streaming = false;
  }
  
  isGenerating = false;
  runBtn.disabled = false;
  renderChatMessages();
}

// ========== Prompt Generator ==========

let promptGeneratorTarget = "message";

function openPromptGenerator(target) {
  promptGeneratorTarget = target;
  const modal = document.getElementById("prompt-generator-modal");
  const inputEl = document.getElementById("prompt-generator-input");
  const resultDiv = document.getElementById("prompt-generator-result");
  const statusEl = document.getElementById("prompt-generator-status");
  
  // Pre-fill with current content
  if (target === "system") {
    inputEl.value = document.getElementById("agent-instructions").value;
  } else {
    inputEl.value = document.getElementById("prompt").value;
  }
  
  resultDiv.style.display = "none";
  statusEl.textContent = "";
  modal.style.display = "flex";
  inputEl.focus();
}

function closePromptGenerator() {
  document.getElementById("prompt-generator-modal").style.display = "none";
}

async function runPromptGenerator() {
  const inputEl = document.getElementById("prompt-generator-input");
  const outputEl = document.getElementById("prompt-generator-output");
  const resultDiv = document.getElementById("prompt-generator-result");
  const statusEl = document.getElementById("prompt-generator-status");
  const runBtn = document.getElementById("prompt-generator-run");
  
  const userInput = inputEl.value.trim();
  if (!userInput) {
    statusEl.textContent = "Please enter a task description or prompt to improve.";
    return;
  }
  
  runBtn.disabled = true;
  statusEl.textContent = "Generating improved prompt...";
  resultDiv.style.display = "none";
  
  try {
    const res = await fetch("/api/prompt-generator", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: userInput }),
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const data = await res.json();
    outputEl.textContent = data.prompt;
    resultDiv.style.display = "block";
    statusEl.textContent = "";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
  
  runBtn.disabled = false;
}

function useGeneratedPrompt(target) {
  const outputEl = document.getElementById("prompt-generator-output");
  const generatedPrompt = outputEl.textContent;
  
  if (target === "system") {
    document.getElementById("agent-instructions").value = generatedPrompt;
    updateSystemCharCount();
  } else {
    document.getElementById("prompt").value = generatedPrompt;
    updatePromptCharCount();
  }
  
  closePromptGenerator();
}

function copyGeneratedPrompt() {
  const outputEl = document.getElementById("prompt-generator-output");
  navigator.clipboard.writeText(outputEl.textContent).then(() => {
    const statusEl = document.getElementById("prompt-generator-status");
    statusEl.textContent = "Copied to clipboard!";
    setTimeout(() => { statusEl.textContent = ""; }, 2000);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initPlaygroundChat();
  initTabs();
  initToolsUI();
  initPromptBuilderUI();
  initABTesterUI();
  initEvaluationUI();
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


// Prompt Builder logic


async function fetchPromptTemplates() {
  const res = await fetch("/api/prompt-templates");
  if (!res.ok) {
    throw new Error(`Failed to fetch prompt templates: ${res.status}`);
  }
  const data = await res.json();
  return data.templates || [];
}


function renderPromptTemplatesTable(templates) {
  const tbody = document.querySelector("#prompt-templates-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  templates.forEach((tpl) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${tpl.id}</td>
      <td>${tpl.name}</td>
      <td>
        <button type="button" data-action="edit" data-id="${tpl.id}">Edit</button>
        <button type="button" data-action="delete" data-id="${tpl.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onPromptTemplatesTableAction);
  });
}


async function onPromptTemplatesTableAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.getAttribute("data-id"));
  const action = btn.getAttribute("data-action");

  if (action === "edit") {
    await populatePromptTemplateForm(id);
  } else if (action === "delete") {
    const confirmed = window.confirm("Delete this template?");
    if (confirmed) {
      await deletePromptTemplate(id);
    }
  }
}


async function populatePromptTemplateForm(id) {
  const templates = await fetchPromptTemplates();
  const tpl = templates.find((t) => t.id === id);
  if (!tpl) return;

  document.getElementById("prompt-template-id").value = tpl.id;
  document.getElementById("prompt-template-name").value = tpl.name || "";
  document.getElementById("prompt-template-description").value = tpl.description || "";
  document.getElementById("prompt-template-system").value = tpl.system_prompt || "";
  document.getElementById("prompt-template-user").value = tpl.user_prompt || "";
  document.getElementById("prompt-template-variables").value = (tpl.variables || []).join(", ");

  updatePromptTemplatePreview();
}


async function deletePromptTemplate(id) {
  await fetch(`/api/prompt-templates/${id}`, { method: "DELETE" });
  await refreshPromptTemplatesUI();
}


async function submitPromptTemplateForm(event) {
  event.preventDefault();
  const messageEl = document.getElementById("prompt-template-message");
  messageEl.textContent = "";

  const id = document.getElementById("prompt-template-id").value;
  const name = document.getElementById("prompt-template-name").value.trim();
  const description = document.getElementById("prompt-template-description").value.trim();
  const systemPrompt = document.getElementById("prompt-template-system").value;
  const userPrompt = document.getElementById("prompt-template-user").value;
  const variablesStr = document.getElementById("prompt-template-variables").value.trim();

  const variables = variablesStr
    ? variablesStr.split(",").map((s) => s.trim()).filter(Boolean)
    : [];

  const payload = {
    name,
    description,
    system_prompt: systemPrompt,
    user_prompt: userPrompt,
    variables,
  };

  const isUpdate = !!id;
  const url = isUpdate ? `/api/prompt-templates/${id}` : "/api/prompt-templates";
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
  await refreshPromptTemplatesUI();
}


function resetPromptTemplateForm() {
  document.getElementById("prompt-template-id").value = "";
  document.getElementById("prompt-template-name").value = "";
  document.getElementById("prompt-template-description").value = "";
  document.getElementById("prompt-template-system").value = "";
  document.getElementById("prompt-template-user").value = "";
  document.getElementById("prompt-template-variables").value = "";
  document.getElementById("prompt-template-vars-json").value = "";
  document.getElementById("prompt-template-preview").textContent = "";
  document.getElementById("prompt-template-message").textContent = "";
}


async function refreshPromptTemplatesUI() {
  const templates = await fetchPromptTemplates();
  renderPromptTemplatesTable(templates);
}


function updatePromptTemplatePreview() {
  const userPrompt = document.getElementById("prompt-template-user").value;
  const varsStr = document.getElementById("prompt-template-vars-json").value.trim();
  const previewEl = document.getElementById("prompt-template-preview");

  let rendered = userPrompt;
  if (varsStr) {
    try {
      const vars = JSON.parse(varsStr);
      Object.entries(vars).forEach(([key, value]) => {
        const re = new RegExp(`{{\\s*${key}\\s*}}`, "g");
        rendered = rendered.replace(re, String(value));
      });
    } catch (err) {
      previewEl.textContent = "Invalid JSON for variable values";
      return;
    }
  }

  previewEl.textContent = rendered;
}


function applyPromptTemplateToPlayground() {
  const previewEl = document.getElementById("prompt-template-preview");
  const promptEl = document.getElementById("prompt");
  const systemEl = document.getElementById("prompt-template-system");
  const agentInstructionsEl = document.getElementById("agent-instructions");

  if (!previewEl || !promptEl) return;

  // Apply rendered user prompt into Playground prompt box
  promptEl.value = previewEl.textContent;

  // Optionally copy system prompt into the Agent Instructions box so it is visible
  if (agentInstructionsEl && systemEl) {
    agentInstructionsEl.value = systemEl.value;
  }
}


function initPromptBuilderUI() {
  const form = document.getElementById("prompt-template-form");
  const resetBtn = document.getElementById("prompt-template-reset-btn");
  const newBtn = document.getElementById("prompt-template-new-btn");
  const varsJsonEl = document.getElementById("prompt-template-vars-json");
  const userPromptEl = document.getElementById("prompt-template-user");
  const applyBtn = document.getElementById("prompt-template-apply-btn");

  if (!form) return;

  form.addEventListener("submit", submitPromptTemplateForm);
  resetBtn.addEventListener("click", resetPromptTemplateForm);
  newBtn.addEventListener("click", resetPromptTemplateForm);
  varsJsonEl.addEventListener("input", updatePromptTemplatePreview);
  userPromptEl.addEventListener("input", updatePromptTemplatePreview);
  applyBtn.addEventListener("click", applyPromptTemplateToPlayground);

  refreshPromptTemplatesUI().catch((err) => {
    const messageEl = document.getElementById("prompt-template-message");
    if (messageEl) {
      messageEl.textContent = `Failed to load prompt templates: ${err}`;
    }
  });
}


// A/B Tester logic

let abVariants = [];

function renderABVariantsList() {
  const container = document.getElementById("ab-variants-list");
  if (!container) return;
  container.innerHTML = "";

  abVariants.forEach((v, idx) => {
    const div = document.createElement("div");
    div.className = "ab-variant-item";
    const label = v.model_name ? `Model: ${v.model_name}` : `Agent: ${v.agent_id}`;
    div.innerHTML = `
      <span>${label}</span>
      <button type="button" data-idx="${idx}" class="ab-remove-variant">✕</button>
    `;
    container.appendChild(div);
  });

  container.querySelectorAll(".ab-remove-variant").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const idx = Number(e.currentTarget.getAttribute("data-idx"));
      abVariants.splice(idx, 1);
      renderABVariantsList();
    });
  });
}

function onABAddVariant() {
  const select = document.getElementById("ab-add-variant-select");
  const val = select.value;
  if (!val) return;

  if (val.startsWith("model:")) {
    abVariants.push({ model_name: val.slice(6) });
  } else if (val.startsWith("agent:")) {
    abVariants.push({ agent_id: val.slice(6) });
  }
  select.value = "";
  renderABVariantsList();
}

async function runABTest() {
  const messageEl = document.getElementById("ab-message");
  const resultsContainer = document.getElementById("ab-results-container");
  const promptEl = document.getElementById("ab-prompt");
  const systemEl = document.getElementById("ab-system-prompt");

  messageEl.textContent = "";
  resultsContainer.innerHTML = "";

  if (abVariants.length < 2) {
    messageEl.textContent = "Please add at least 2 variants to compare.";
    return;
  }

  const payload = {
    prompt: promptEl.value,
    system_prompt: systemEl.value,
    variants: abVariants,
  };

  messageEl.textContent = "Running...";

  try {
    const res = await fetch("/api/ab-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      messageEl.textContent = `Error: ${res.status}`;
      return;
    }

    const data = await res.json();
    messageEl.textContent = "";
    renderABResults(data.results);
  } catch (err) {
    messageEl.textContent = `Request failed: ${err}`;
  }
}

function renderABResults(results) {
  const container = document.getElementById("ab-results-container");
  container.innerHTML = "";

  results.forEach((r, idx) => {
    const card = document.createElement("div");
    card.className = "ab-result-card";

    const title = r.agent_name
      ? `Agent: ${r.agent_name}`
      : `Model: ${r.model_name}`;

    card.innerHTML = `
      <h4>${title}</h4>
      <pre class="ab-response">${r.error ? `Error: ${r.error}` : r.response}</pre>
      <div class="ab-meta">Latency: ${r.latency_ms.toFixed(1)} ms</div>
      <div class="ab-feedback">
        <button type="button" data-idx="${idx}" data-vote="better">👍 Better</button>
        <button type="button" data-idx="${idx}" data-vote="worse">👎 Worse</button>
      </div>
    `;
    container.appendChild(card);
  });

  container.querySelectorAll(".ab-feedback button").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const vote = e.currentTarget.getAttribute("data-vote");
      e.currentTarget.parentElement.innerHTML = `<span>Voted: ${vote}</span>`;
    });
  });
}

function initABTesterUI() {
  const addSelect = document.getElementById("ab-add-variant-select");
  const runBtn = document.getElementById("ab-run-btn");

  if (!addSelect || !runBtn) return;

  addSelect.addEventListener("change", onABAddVariant);
  runBtn.addEventListener("click", runABTest);

  renderABVariantsList();
}


// ========== Evaluation Suite UI ==========

let currentDatasetId = null;

const DATASET_TEMPLATES = {
  "qa-factual": {
    name: "Factual Q&A Dataset",
    description: "Test factual knowledge and accuracy",
    rows: [
      {"query": "What is the capital of France?", "ground_truth": "Paris"},
      {"query": "Who wrote Romeo and Juliet?", "ground_truth": "William Shakespeare"},
      {"query": "What is the largest planet in our solar system?", "ground_truth": "Jupiter"},
      {"query": "In what year did World War II end?", "ground_truth": "1945"},
      {"query": "What is the chemical symbol for gold?", "ground_truth": "Au"}
    ]
  },
  "qa-math": {
    name: "Math Q&A Dataset",
    description: "Test mathematical reasoning and calculations",
    rows: [
      {"query": "What is 15 + 27?", "ground_truth": "42"},
      {"query": "What is 144 divided by 12?", "ground_truth": "12"},
      {"query": "What is the square root of 81?", "ground_truth": "9"},
      {"query": "If a rectangle has length 8 and width 5, what is its area?", "ground_truth": "40"},
      {"query": "What is 25% of 200?", "ground_truth": "50"}
    ]
  },
  "summarization": {
    name: "Summarization Dataset",
    description: "Test text summarization capabilities",
    rows: [
      {"query": "Summarize: The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is often used for typing practice.", "ground_truth": "A pangram sentence used for typing practice."},
      {"query": "Summarize: Machine learning is a subset of artificial intelligence that enables systems to learn from data. It uses algorithms to identify patterns and make decisions with minimal human intervention.", "ground_truth": "Machine learning is an AI subset that learns from data to identify patterns and make decisions."},
      {"query": "Summarize: Climate change refers to long-term shifts in global temperatures and weather patterns. Human activities have been the main driver since the 1800s, primarily due to burning fossil fuels.", "ground_truth": "Climate change involves long-term temperature shifts, mainly caused by human fossil fuel use since the 1800s."}
    ]
  },
  "sentiment": {
    name: "Sentiment Analysis Dataset",
    description: "Test sentiment classification accuracy",
    rows: [
      {"query": "Classify the sentiment: I absolutely love this product! Best purchase ever.", "ground_truth": "positive"},
      {"query": "Classify the sentiment: This is the worst experience I've ever had. Terrible service.", "ground_truth": "negative"},
      {"query": "Classify the sentiment: The movie was okay, nothing special but not bad either.", "ground_truth": "neutral"},
      {"query": "Classify the sentiment: Amazing quality and fast shipping! Highly recommend!", "ground_truth": "positive"},
      {"query": "Classify the sentiment: Disappointed with the results. Would not buy again.", "ground_truth": "negative"}
    ]
  },
  "translation": {
    name: "Translation Dataset",
    description: "Test translation accuracy (English to Spanish)",
    rows: [
      {"query": "Translate to Spanish: Hello, how are you?", "ground_truth": "Hola, \u00bfc\u00f3mo est\u00e1s?"},
      {"query": "Translate to Spanish: Thank you very much.", "ground_truth": "Muchas gracias."},
      {"query": "Translate to Spanish: Where is the library?", "ground_truth": "\u00bfD\u00f3nde est\u00e1 la biblioteca?"},
      {"query": "Translate to Spanish: I love learning new languages.", "ground_truth": "Me encanta aprender nuevos idiomas."},
      {"query": "Translate to Spanish: Good morning, my friend.", "ground_truth": "Buenos d\u00edas, mi amigo."}
    ]
  },
  "code-generation": {
    name: "Code Generation Dataset",
    description: "Test code generation and programming tasks",
    rows: [
      {"query": "Write a Python function to calculate factorial of n.", "ground_truth": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"},
      {"query": "Write a Python function to check if a string is a palindrome.", "ground_truth": "def is_palindrome(s):\n    return s == s[::-1]"},
      {"query": "Write a Python function to find the maximum value in a list.", "ground_truth": "def find_max(lst):\n    return max(lst)"},
      {"query": "Write a Python function to reverse a string.", "ground_truth": "def reverse_string(s):\n    return s[::-1]"}
    ]
  },
  "classification": {
    name: "Text Classification Dataset",
    description: "Test topic/category classification",
    rows: [
      {"query": "Classify the topic: The stock market reached new highs today as tech companies reported strong earnings.", "ground_truth": "finance"},
      {"query": "Classify the topic: The team won the championship after an exciting overtime victory.", "ground_truth": "sports"},
      {"query": "Classify the topic: Scientists discovered a new species of deep-sea fish near the Mariana Trench.", "ground_truth": "science"},
      {"query": "Classify the topic: The new smartphone features an improved camera and longer battery life.", "ground_truth": "technology"},
      {"query": "Classify the topic: The recipe calls for fresh herbs, olive oil, and garlic.", "ground_truth": "food"}
    ]
  },
  "rag": {
    name: "RAG - Retrieval QA Dataset",
    description: "Test retrieval-augmented generation with context",
    rows: [
      {"query": "Context: Paris is the capital of France. It is known for the Eiffel Tower. Question: What is Paris known for?", "ground_truth": "The Eiffel Tower"},
      {"query": "Context: Python was created by Guido van Rossum and first released in 1991. Question: Who created Python?", "ground_truth": "Guido van Rossum"},
      {"query": "Context: The human body has 206 bones. The largest bone is the femur. Question: How many bones are in the human body?", "ground_truth": "206"},
      {"query": "Context: Water boils at 100\u00b0C at sea level. At higher altitudes, water boils at lower temperatures. Question: At what temperature does water boil at sea level?", "ground_truth": "100\u00b0C"}
    ]
  }
};

function loadDatasetTemplate(templateId) {
  if (!templateId || !DATASET_TEMPLATES[templateId]) return;
  
  const template = DATASET_TEMPLATES[templateId];
  document.getElementById("dataset-name").value = template.name;
  document.getElementById("dataset-description").value = template.description;
  
  const jsonl = template.rows.map(r => JSON.stringify(r)).join("\n");
  document.getElementById("dataset-rows").value = jsonl;
  
  // Reset the select
  document.getElementById("dataset-template-select").value = "";
  document.getElementById("dataset-message").textContent = "Template loaded! Edit as needed.";
}

async function fetchDatasets() {
  const res = await fetch("/api/datasets");
  if (!res.ok) throw new Error(`Failed to fetch datasets: ${res.status}`);
  const data = await res.json();
  return data.datasets || [];
}

async function fetchEvaluators() {
  const res = await fetch("/api/evaluators");
  if (!res.ok) throw new Error(`Failed to fetch evaluators: ${res.status}`);
  const data = await res.json();
  return data.evaluators || [];
}

async function fetchEvalJobs() {
  const res = await fetch("/api/eval-jobs");
  if (!res.ok) throw new Error(`Failed to fetch eval jobs: ${res.status}`);
  const data = await res.json();
  return data.jobs || [];
}

function renderDatasetsTable(datasets) {
  const tbody = document.querySelector("#datasets-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  datasets.forEach((ds) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${ds.id}</td>
      <td>${ds.name}</td>
      <td>${ds.rows ? ds.rows.length : 0}</td>
      <td>
        <button type="button" data-action="edit" data-id="${ds.id}">Edit</button>
        <button type="button" data-action="delete" data-id="${ds.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onDatasetTableAction);
  });
}

async function onDatasetTableAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.getAttribute("data-id"));
  const action = btn.getAttribute("data-action");

  if (action === "edit") {
    await populateDatasetForm(id);
  } else if (action === "delete") {
    if (window.confirm("Delete this dataset?")) {
      await fetch(`/api/datasets/${id}`, { method: "DELETE" });
      await refreshEvaluationUI();
    }
  }
}

async function populateDatasetForm(id) {
  const datasets = await fetchDatasets();
  const ds = datasets.find((d) => d.id === id);
  if (!ds) return;

  currentDatasetId = id;
  document.getElementById("dataset-id").value = ds.id;
  document.getElementById("dataset-name").value = ds.name || "";
  document.getElementById("dataset-description").value = ds.description || "";

  // Convert rows to JSONL
  const jsonl = (ds.rows || []).map((r) => JSON.stringify(r)).join("\n");
  document.getElementById("dataset-rows").value = jsonl;

  // Show dataset editor
  document.getElementById("dataset-editor").style.display = "block";
  document.getElementById("evaluator-editor").style.display = "none";
}

async function submitDatasetForm(event) {
  event.preventDefault();
  const messageEl = document.getElementById("dataset-message");
  messageEl.textContent = "";

  const id = document.getElementById("dataset-id").value;
  const name = document.getElementById("dataset-name").value.trim();
  const description = document.getElementById("dataset-description").value.trim();
  const rowsText = document.getElementById("dataset-rows").value.trim();

  // Parse JSONL
  let rows = [];
  if (rowsText) {
    try {
      rows = rowsText.split("\n").filter(Boolean).map((line) => JSON.parse(line));
    } catch (err) {
      messageEl.textContent = "Invalid JSONL format";
      return;
    }
  }

  const payload = { name, description, rows };
  const isUpdate = !!id;
  const url = isUpdate ? `/api/datasets/${id}` : "/api/datasets";
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

  const saved = await res.json();
  currentDatasetId = saved.id;
  document.getElementById("dataset-id").value = saved.id;
  messageEl.textContent = "Saved";
  await refreshEvaluationUI();
}

function resetDatasetForm() {
  currentDatasetId = null;
  document.getElementById("dataset-id").value = "";
  document.getElementById("dataset-name").value = "";
  document.getElementById("dataset-description").value = "";
  document.getElementById("dataset-rows").value = "";
  document.getElementById("dataset-message").textContent = "";
}

async function runBulkGenerate() {
  const messageEl = document.getElementById("bulk-run-message");
  const progressContainer = document.getElementById("bulk-run-progress");
  const progressBar = document.getElementById("bulk-run-progress-bar");
  const progressText = document.getElementById("bulk-run-progress-text");
  const liveContainer = document.getElementById("bulk-run-live");
  const liveList = document.getElementById("bulk-run-live-list");
  
  messageEl.textContent = "";

  const datasetId = document.getElementById("dataset-id").value;
  if (!datasetId) {
    messageEl.textContent = "Save the dataset first";
    return;
  }

  const modelName = document.getElementById("bulk-run-model").value;
  const agentId = document.getElementById("bulk-run-agent").value;

  if (!modelName && !agentId) {
    messageEl.textContent = "Select a model or agent";
    return;
  }

  // Show progress UI
  progressContainer.style.display = "block";
  liveContainer.style.display = "block";
  liveList.innerHTML = "";
  progressBar.style.width = "0%";
  progressText.textContent = "Starting...";
  messageEl.textContent = "";

  const payload = {
    dataset_id: Number(datasetId),
    model_name: modelName || null,
    agent_id: agentId || null,
  };

  try {
    const response = await fetch(`/api/datasets/${datasetId}/bulk-run-stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.done) {
              progressBar.style.width = "100%";
              progressText.textContent = "Complete!";
              messageEl.textContent = "Done! Responses generated.";
              messageEl.style.color = "#4ade80";
              
              // Refresh the dataset rows
              await refreshEvaluationUI();
              await populateDatasetForm(Number(datasetId));
              continue;
            }

            if (data.error) {
              messageEl.textContent = `Error: ${data.error}`;
              messageEl.style.color = "#f87171";
              continue;
            }

            if (data.type === "progress") {
              const pct = ((data.index + 1) / data.total * 100).toFixed(0);
              progressBar.style.width = `${pct}%`;
              progressText.textContent = `Processing ${data.index + 1} of ${data.total}: ${data.query}`;
            }

            if (data.type === "response") {
              const item = document.createElement("div");
              item.className = "bulk-run-live-item" + (data.error ? " error" : "");
              item.innerHTML = `
                <div class="live-item-header">
                  <span class="live-item-index">#${data.index + 1}</span>
                  <span class="live-item-query">${escapeHtml(data.query.substring(0, 80))}${data.query.length > 80 ? "..." : ""}</span>
                </div>
                <div class="live-item-response">${escapeHtml(data.response.substring(0, 200))}${data.response.length > 200 ? "..." : ""}</div>
                ${data.ground_truth ? `<div class="live-item-truth">Expected: ${escapeHtml(data.ground_truth.substring(0, 100))}</div>` : ""}
              `;
              liveList.insertBefore(item, liveList.firstChild);
              
              // Keep only last 10 items visible
              while (liveList.children.length > 10) {
                liveList.removeChild(liveList.lastChild);
              }
            }
          } catch (e) {
            console.error("Failed to parse SSE data:", e);
          }
        }
      }
    }
  } catch (err) {
    messageEl.textContent = `Bulk run failed: ${err}`;
    messageEl.style.color = "#f87171";
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderEvaluatorsList(evaluators) {
  const container = document.getElementById("evaluators-list");
  if (!container) return;
  container.innerHTML = "";

  evaluators.forEach((ev) => {
    const div = document.createElement("div");
    div.className = "evaluator-item";
    const typeLabel = ev.type === "builtin" ? "📊" : ev.type === "llm" ? "🤖" : "🐍";
    div.innerHTML = `
      <span>${typeLabel} ${ev.name}</span>
      ${ev.type !== "builtin" ? `<button type="button" data-action="edit" data-id="${ev.id}">Edit</button>
      <button type="button" data-action="delete" data-id="${ev.id}">Delete</button>` : ""}
    `;
    container.appendChild(div);
  });

  container.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onEvaluatorAction);
  });
}

async function onEvaluatorAction(event) {
  const btn = event.currentTarget;
  const id = btn.getAttribute("data-id");
  const action = btn.getAttribute("data-action");

  // Extract numeric ID from "custom:X"
  const numericId = id.startsWith("custom:") ? Number(id.split(":")[1]) : Number(id);

  if (action === "edit") {
    await populateEvaluatorForm(numericId);
  } else if (action === "delete") {
    if (window.confirm("Delete this evaluator?")) {
      await fetch(`/api/evaluators/custom/${numericId}`, { method: "DELETE" });
      await refreshEvaluationUI();
    }
  }
}

async function populateEvaluatorForm(id) {
  const res = await fetch(`/api/evaluators/custom/${id}`);
  if (!res.ok) return;
  const ev = await res.json();

  document.getElementById("evaluator-id").value = ev.id;
  document.getElementById("evaluator-name").value = ev.name || "";
  document.getElementById("evaluator-description").value = ev.description || "";
  document.getElementById("evaluator-type").value = ev.evaluator_type || "llm";
  document.getElementById("evaluator-llm-prompt").value = ev.llm_prompt || "";
  document.getElementById("evaluator-code").value = ev.code || "";

  updateEvaluatorTypeVisibility();

  document.getElementById("dataset-editor").style.display = "none";
  document.getElementById("evaluator-editor").style.display = "block";
}

function updateEvaluatorTypeVisibility() {
  const type = document.getElementById("evaluator-type").value;
  document.getElementById("evaluator-llm-section").style.display = type === "llm" ? "block" : "none";
  document.getElementById("evaluator-code-section").style.display = type === "code" ? "block" : "none";
}

async function submitEvaluatorForm(event) {
  event.preventDefault();
  const messageEl = document.getElementById("evaluator-message");
  messageEl.textContent = "";

  const id = document.getElementById("evaluator-id").value;
  const name = document.getElementById("evaluator-name").value.trim();
  const description = document.getElementById("evaluator-description").value.trim();
  const evaluatorType = document.getElementById("evaluator-type").value;
  const llmPrompt = document.getElementById("evaluator-llm-prompt").value;
  const code = document.getElementById("evaluator-code").value;

  const payload = {
    name,
    description,
    evaluator_type: evaluatorType,
    llm_prompt: llmPrompt,
    code,
  };

  const isUpdate = !!id;
  const url = isUpdate ? `/api/evaluators/custom/${id}` : "/api/evaluators/custom";
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
  await refreshEvaluationUI();
  cancelEvaluatorForm();
}

function cancelEvaluatorForm() {
  document.getElementById("evaluator-id").value = "";
  document.getElementById("evaluator-name").value = "";
  document.getElementById("evaluator-description").value = "";
  document.getElementById("evaluator-type").value = "llm";
  document.getElementById("evaluator-llm-prompt").value = "";
  document.getElementById("evaluator-code").value = "";
  document.getElementById("evaluator-message").textContent = "";
  updateEvaluatorTypeVisibility();

  document.getElementById("evaluator-editor").style.display = "none";
  document.getElementById("dataset-editor").style.display = "block";
}

function showNewEvaluatorForm() {
  cancelEvaluatorForm();
  document.getElementById("dataset-editor").style.display = "none";
  document.getElementById("evaluator-editor").style.display = "block";
}

async function populateEvalJobSelects() {
  const datasets = await fetchDatasets();
  const evaluators = await fetchEvaluators();

  const datasetSelect = document.getElementById("eval-job-dataset");
  datasetSelect.innerHTML = '<option value="">-- Select Dataset --</option>';
  datasets.forEach((ds) => {
    const opt = document.createElement("option");
    opt.value = ds.id;
    opt.textContent = `${ds.name} (${ds.rows ? ds.rows.length : 0} rows)`;
    datasetSelect.appendChild(opt);
  });

  const evaluatorsSelect = document.getElementById("eval-job-evaluators");
  evaluatorsSelect.innerHTML = "";
  evaluators.forEach((ev) => {
    const opt = document.createElement("option");
    opt.value = ev.id;
    opt.textContent = ev.name;
    evaluatorsSelect.appendChild(opt);
  });
}

function renderEvalJobsList(jobs) {
  const container = document.getElementById("eval-jobs-list");
  if (!container) return;
  container.innerHTML = "";

  jobs.slice().reverse().forEach((job) => {
    const div = document.createElement("div");
    div.className = "eval-job-item";
    const statusIcon = job.status === "completed" ? "✅" : job.status === "running" ? "⏳" : job.status === "failed" ? "❌" : "⏸️";
    div.innerHTML = `
      <span>${statusIcon} ${job.name}</span>
      <span class="eval-job-date">${new Date(job.created_at).toLocaleString()}</span>
      <button type="button" data-action="view" data-id="${job.id}">View</button>
      <button type="button" data-action="delete" data-id="${job.id}">Delete</button>
    `;
    container.appendChild(div);
  });

  container.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onEvalJobAction);
  });
}

async function onEvalJobAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.getAttribute("data-id"));
  const action = btn.getAttribute("data-action");

  if (action === "view") {
    await showEvalJobResults(id);
  } else if (action === "delete") {
    if (window.confirm("Delete this job?")) {
      await fetch(`/api/eval-jobs/${id}`, { method: "DELETE" });
      await refreshEvaluationUI();
    }
  }
}

async function showEvalJobResults(jobId) {
  const res = await fetch(`/api/eval-jobs/${jobId}`);
  if (!res.ok) return;
  const job = await res.json();

  document.getElementById("eval-results-title").textContent = job.name;

  // Aggregate scores
  const aggregateDiv = document.getElementById("eval-aggregate-scores");
  aggregateDiv.innerHTML = "";
  if (job.aggregate_scores) {
    for (const [evId, score] of Object.entries(job.aggregate_scores)) {
      const span = document.createElement("span");
      span.className = "aggregate-score";
      span.textContent = `${evId}: ${(score * 100).toFixed(1)}%`;
      aggregateDiv.appendChild(span);
    }
  }

  // Results table
  const tbody = document.querySelector("#eval-results-table tbody");
  tbody.innerHTML = "";
  (job.results || []).forEach((r) => {
    const tr = document.createElement("tr");
    tr.className = r.error ? "error-row" : "";
    tr.innerHTML = `
      <td>${r.row_index}</td>
      <td>${r.evaluator_id}</td>
      <td>${(r.score * 100).toFixed(1)}%</td>
      <td>${r.reason}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById("eval-results-view").style.display = "block";
}

function closeEvalResultsView() {
  document.getElementById("eval-results-view").style.display = "none";
}

async function createAndRunEvalJob() {
  const messageEl = document.getElementById("eval-job-message");
  messageEl.textContent = "";

  const name = document.getElementById("eval-job-name").value.trim() || "Evaluation " + new Date().toLocaleString();
  const datasetId = document.getElementById("eval-job-dataset").value;
  const evaluatorsSelect = document.getElementById("eval-job-evaluators");
  const selectedEvaluators = Array.from(evaluatorsSelect.selectedOptions).map((o) => o.value);

  if (!datasetId) {
    messageEl.textContent = "Select a dataset";
    return;
  }
  if (selectedEvaluators.length === 0) {
    messageEl.textContent = "Select at least one evaluator";
    return;
  }

  const payload = {
    name,
    dataset_id: Number(datasetId),
    evaluator_ids: selectedEvaluators,
  };

  messageEl.textContent = "Creating job...";

  // Create job
  let res = await fetch("/api/eval-jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    messageEl.textContent = `Create failed: ${res.status}`;
    return;
  }

  const job = await res.json();
  messageEl.textContent = "Running evaluation...";

  // Run job
  res = await fetch(`/api/eval-jobs/${job.id}/run`, { method: "POST" });
  if (!res.ok) {
    messageEl.textContent = `Run failed: ${res.status}`;
    await refreshEvaluationUI();
    return;
  }

  messageEl.textContent = "Done!";
  await refreshEvaluationUI();
  await showEvalJobResults(job.id);
}

async function refreshEvaluationUI() {
  const datasets = await fetchDatasets();
  const evaluators = await fetchEvaluators();
  const jobs = await fetchEvalJobs();

  renderDatasetsTable(datasets);
  renderEvaluatorsList(evaluators);
  renderEvalJobsList(jobs);
  await populateEvalJobSelects();
}

function initEvaluationUI() {
  const datasetForm = document.getElementById("dataset-form");
  const datasetResetBtn = document.getElementById("dataset-reset-btn");
  const datasetNewBtn = document.getElementById("dataset-new-btn");
  const bulkRunBtn = document.getElementById("bulk-run-btn");

  const evaluatorForm = document.getElementById("evaluator-form");
  const evaluatorNewBtn = document.getElementById("evaluator-new-btn");
  const evaluatorCancelBtn = document.getElementById("evaluator-cancel-btn");
  const evaluatorTypeSelect = document.getElementById("evaluator-type");

  const evalJobCreateBtn = document.getElementById("eval-job-create-btn");
  const evalResultsCloseBtn = document.getElementById("eval-results-close-btn");

  if (!datasetForm) return;

  const datasetTemplateSelect = document.getElementById("dataset-template-select");

  datasetForm.addEventListener("submit", submitDatasetForm);
  datasetResetBtn.addEventListener("click", resetDatasetForm);
  datasetNewBtn.addEventListener("click", () => {
    resetDatasetForm();
    document.getElementById("dataset-editor").style.display = "block";
    document.getElementById("evaluator-editor").style.display = "none";
  });
  datasetTemplateSelect.addEventListener("change", (e) => loadDatasetTemplate(e.target.value));
  bulkRunBtn.addEventListener("click", runBulkGenerate);

  evaluatorForm.addEventListener("submit", submitEvaluatorForm);
  evaluatorNewBtn.addEventListener("click", showNewEvaluatorForm);
  evaluatorCancelBtn.addEventListener("click", cancelEvaluatorForm);
  evaluatorTypeSelect.addEventListener("change", updateEvaluatorTypeVisibility);

  evalJobCreateBtn.addEventListener("click", createAndRunEvalJob);
  evalResultsCloseBtn.addEventListener("click", closeEvalResultsView);

  refreshEvaluationUI().catch((err) => {
    console.error("Failed to load evaluation data:", err);
  });
}
