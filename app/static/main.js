// ========== Interactive Playground Chat ==========

let chatHistory = [];
let attachments = [];
let isGenerating = false;

function initPlaygroundChat() {
  console.log("initPlaygroundChat started");
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

  // Debug: log all elements
  console.log("Elements found:", {
    runBtn: !!runBtn,
    promptEl: !!promptEl,
    clearChatBtn: !!clearChatBtn,
    attachBtn: !!attachBtn,
    fileInput: !!fileInput,
    agentSelect: !!agentSelect,
    systemPromptEl: !!systemPromptEl,
    improveSystemBtn: !!improveSystemBtn,
    improvePromptBtn: !!improvePromptBtn,
  });

  if (!runBtn) {
    console.error("run-btn not found!");
    return;
  }
  if (!promptEl) {
    console.error("prompt textarea not found!");
    return;
  }

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
  console.log("=== renderChatMessages v4 ===", "history:", chatHistory.length);
  
  if (!container) {
    console.error("chat-messages container not found!");
    return;
  }
  
  console.log("Container found, innerHTML before:", container.innerHTML.substring(0, 100));
  
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
  console.log("Cleared container, now adding messages...");
  
  chatHistory.forEach((msg, idx) => {
    const div = document.createElement("div");
    div.className = `chat-message ${msg.role}`;
    div.id = `message-${idx}`;
    
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = msg.role === "user" ? "👤" : "🤖";
    
    const content = document.createElement("div");
    content.className = "message-content";
    if (msg.streaming) {
      content.classList.add("message-streaming");
    }
    
    const text = document.createElement("div");
    text.className = "message-text";
    text.textContent = msg.content || (msg.streaming ? "" : "");
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
    console.log("Appended message:", msg.role, msg.content?.substring(0, 50));
  });
  
  // Scroll to bottom
  console.log("Container scrollHeight:", container.scrollHeight, "clientHeight:", container.clientHeight);
  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  console.log("sendMessage called");
  const promptEl = document.getElementById("prompt");
  const runBtn = document.getElementById("run-btn");
  const userMessage = promptEl.value.trim();
  
  console.log("userMessage:", userMessage, "attachments:", attachments.length);
  
  if (!userMessage && attachments.length === 0) {
    console.log("No message or attachments, returning");
    return;
  }
  if (isGenerating) {
    console.log("Already generating, returning");
    return;
  }
  
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
  
  const msgIdx = chatHistory.length - 1;
  
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
    
    console.log("Stream mode:", streamModeEl.checked, "Payload:", payload);
    
    if (streamModeEl.checked) {
      // Streaming response
      console.log("Using streaming mode");
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      console.log("Response status:", response.status);
      
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
        console.log("Stream chunk:", done, value ? value.length : 0);
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        console.log("Buffer:", buffer);
        const lines = buffer.split("\n");
        buffer = lines.pop();
        
        for (const line of lines) {
          console.log("Processing line:", line);
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              console.log("Parsed data:", data);
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
      
      console.log("Stream complete. fullContent:", fullContent);
      chatHistory[msgIdx].content = fullContent;
      chatHistory[msgIdx].streaming = false;
      chatHistory[msgIdx].meta = meta;
      console.log("Final chatHistory:", JSON.stringify(chatHistory));
    } else {
      // Non-streaming response
      console.log("Using non-streaming mode");
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      console.log("Response status:", res.status);
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Response data:", data);
      chatHistory[msgIdx].content = data.response;
      chatHistory[msgIdx].streaming = false;
      chatHistory[msgIdx].meta = {
        model: data.model_name,
        latency_ms: data.latency_ms,
      };
      console.log("Updated chatHistory:", JSON.stringify(chatHistory));
    }
  } catch (err) {
    console.error("sendMessage error:", err);
    chatHistory[msgIdx].content = `Error: ${err.message}`;
    chatHistory[msgIdx].streaming = false;
  }
  
  isGenerating = false;
  runBtn.disabled = false;
  console.log("About to call final renderChatMessages, chatHistory:", chatHistory.length);
  renderChatMessages();
  console.log("Final renderChatMessages completed");
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
  initOrchestratorUI();
  initChatLabUI();
  initGuardrailsUI();
  initHistoryUI();
  initDashboardUI();
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


async function fetchPromptTemplates(includePresets = false, category = null) {
  let url = "/api/prompt-templates?include_presets=" + includePresets;
  if (category) {
    url += "&category=" + encodeURIComponent(category);
  }
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch prompt templates: ${res.status}`);
  }
  const data = await res.json();
  return data.templates || [];
}

async function fetchPresetTemplates(category = null) {
  return fetchPromptTemplates(true, category);
}

function renderPresetTemplatesGrid(templates) {
  const grid = document.getElementById("preset-templates-grid");
  if (!grid) return;
  grid.innerHTML = "";

  // Filter out user templates (negative IDs are presets)
  const presets = templates.filter(t => t.id < 0);
  
  if (presets.length === 0) {
    grid.innerHTML = '<p style="color:#9ca3af;">No preset templates in this category.</p>';
    return;
  }

  presets.forEach((tpl) => {
    const card = document.createElement("div");
    card.className = "preset-template-card";
    card.dataset.id = tpl.id;
    
    const categoryLabel = getCategoryLabel(tpl.category);
    const varsHtml = (tpl.variables || []).map(v => `<span>{{${v}}}</span>`).join("");
    
    card.innerHTML = `
      <div class="card-category">${categoryLabel}</div>
      <div class="card-name">${escapeHtml(tpl.name)}</div>
      <div class="card-desc">${escapeHtml(tpl.description || "")}</div>
      ${varsHtml ? `<div class="card-vars">${varsHtml}</div>` : ""}
    `;
    
    card.addEventListener("click", () => loadPresetTemplate(tpl));
    grid.appendChild(card);
  });
}

function getCategoryLabel(category) {
  const labels = {
    roleplay: "🎭 Role-Play",
    cot: "🧠 Chain-of-Thought",
    fewshot: "📚 Few-Shot",
    general: "⚙️ General",
    custom: "📝 Custom"
  };
  return labels[category] || category;
}

function loadPresetTemplate(tpl) {
  // Populate form with preset values
  document.getElementById("prompt-template-id").value = ""; // New template based on preset
  document.getElementById("prompt-template-name").value = tpl.name + " (Copy)";
  document.getElementById("prompt-template-category").value = tpl.category || "custom";
  document.getElementById("prompt-template-description").value = tpl.description || "";
  document.getElementById("prompt-template-system").value = tpl.system_prompt || "";
  document.getElementById("prompt-template-user").value = tpl.user_prompt || "";
  document.getElementById("prompt-template-variables").value = (tpl.variables || []).join(", ");
  
  // Build sample vars JSON
  const sampleVars = {};
  (tpl.variables || []).forEach(v => {
    sampleVars[v] = `[${v}]`;
  });
  document.getElementById("prompt-template-vars-json").value = 
    Object.keys(sampleVars).length > 0 ? JSON.stringify(sampleVars, null, 2) : "";
  
  updatePromptTemplatePreview();
  
  // Highlight selected card
  document.querySelectorAll(".preset-template-card").forEach(c => c.classList.remove("selected"));
  const selectedCard = document.querySelector(`.preset-template-card[data-id="${tpl.id}"]`);
  if (selectedCard) selectedCard.classList.add("selected");
  
  // Scroll to editor
  document.querySelector(".prompt-template-editor")?.scrollIntoView({ behavior: "smooth" });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderPromptTemplatesTable(templates) {
  const tbody = document.querySelector("#prompt-templates-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  // Only show user templates (positive IDs)
  const userTemplates = templates.filter(t => t.id > 0);
  
  if (userTemplates.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="color:#9ca3af;text-align:center;">No saved templates yet. Create one or load from presets.</td></tr>';
    return;
  }

  userTemplates.forEach((tpl) => {
    const tr = document.createElement("tr");
    const categoryLabel = getCategoryLabel(tpl.category);
    tr.innerHTML = `
      <td>${tpl.id}</td>
      <td>${escapeHtml(tpl.name)}</td>
      <td>${categoryLabel}</td>
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
  const templates = await fetchPromptTemplates(false); // Only user templates for editing
  const tpl = templates.find((t) => t.id === id);
  if (!tpl) return;

  document.getElementById("prompt-template-id").value = tpl.id;
  document.getElementById("prompt-template-name").value = tpl.name || "";
  document.getElementById("prompt-template-category").value = tpl.category || "custom";
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
  const category = document.getElementById("prompt-template-category").value;
  const description = document.getElementById("prompt-template-description").value.trim();
  const systemPrompt = document.getElementById("prompt-template-system").value;
  const userPrompt = document.getElementById("prompt-template-user").value;
  const variablesStr = document.getElementById("prompt-template-variables").value.trim();

  const variables = variablesStr
    ? variablesStr.split(",").map((s) => s.trim()).filter(Boolean)
    : [];

  const payload = {
    name,
    category,
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
  document.getElementById("prompt-template-category").value = "custom";
  document.getElementById("prompt-template-description").value = "";
  document.getElementById("prompt-template-system").value = "";
  document.getElementById("prompt-template-user").value = "";
  document.getElementById("prompt-template-variables").value = "";
  document.getElementById("prompt-template-vars-json").value = "";
  document.getElementById("prompt-template-preview").textContent = "";
  document.getElementById("prompt-template-message").textContent = "";
  
  // Clear preset selection
  document.querySelectorAll(".preset-template-card").forEach(c => c.classList.remove("selected"));
}


async function refreshPromptTemplatesUI() {
  // Fetch user templates for the table
  const userTemplates = await fetchPromptTemplates(false);
  renderPromptTemplatesTable(userTemplates);
  
  // Fetch all (including presets) for the preset grid
  const allTemplates = await fetchPromptTemplates(true);
  renderPresetTemplatesGrid(allTemplates);
}

async function filterPresetsByCategory(category) {
  const templates = category === "all" 
    ? await fetchPromptTemplates(true) 
    : await fetchPromptTemplates(true, category);
  renderPresetTemplatesGrid(templates);
}

async function filterUserTemplatesByCategory(category) {
  const templates = category 
    ? await fetchPromptTemplates(false, category) 
    : await fetchPromptTemplates(false);
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
  
  // Update character counts
  updatePromptCharCount();
  updateSystemCharCount();
  
  // Switch to Playground tab
  const playgroundBtn = document.querySelector('[data-tab="playground-tab"]');
  if (playgroundBtn) {
    playgroundBtn.click();
  }
}


function initPromptBuilderUI() {
  const form = document.getElementById("prompt-template-form");
  const resetBtn = document.getElementById("prompt-template-reset-btn");
  const newBtn = document.getElementById("prompt-template-new-btn");
  const varsJsonEl = document.getElementById("prompt-template-vars-json");
  const userPromptEl = document.getElementById("prompt-template-user");
  const applyBtn = document.getElementById("prompt-template-apply-btn");
  const categoryFilter = document.getElementById("template-category-filter");

  if (!form) return;

  form.addEventListener("submit", submitPromptTemplateForm);
  resetBtn.addEventListener("click", resetPromptTemplateForm);
  newBtn.addEventListener("click", resetPromptTemplateForm);
  varsJsonEl.addEventListener("input", updatePromptTemplatePreview);
  userPromptEl.addEventListener("input", updatePromptTemplatePreview);
  applyBtn.addEventListener("click", applyPromptTemplateToPlayground);
  
  // Category filter for user templates
  if (categoryFilter) {
    categoryFilter.addEventListener("change", (e) => {
      filterUserTemplatesByCategory(e.target.value);
    });
  }
  
  // Preset category tabs
  document.querySelectorAll(".preset-cat-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".preset-cat-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      filterPresetsByCategory(e.target.dataset.category);
    });
  });

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


// ========== Agent Orchestrator UI ==========

let workflowNodes = [];
let workflowEdges = [];
let selectedNodeId = null;
let nodeIdCounter = 1;

async function fetchWorkflows() {
  const res = await fetch("/api/workflows");
  if (!res.ok) throw new Error(`Failed to fetch workflows: ${res.status}`);
  const data = await res.json();
  return data.workflows || [];
}

async function fetchWorkflowRuns(workflowId = null) {
  const url = workflowId ? `/api/workflow-runs?workflow_id=${workflowId}` : "/api/workflow-runs";
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch workflow runs: ${res.status}`);
  const data = await res.json();
  return data.runs || [];
}

function renderWorkflowsTable(workflows) {
  const tbody = document.querySelector("#workflows-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  workflows.forEach((wf) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${wf.id}</td>
      <td>${wf.name}</td>
      <td>${wf.nodes ? wf.nodes.length : 0}</td>
      <td>
        <button type="button" data-action="edit" data-id="${wf.id}">Edit</button>
        <button type="button" data-action="delete" data-id="${wf.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onWorkflowTableAction);
  });
}

async function onWorkflowTableAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.getAttribute("data-id"));
  const action = btn.getAttribute("data-action");

  if (action === "edit") {
    await loadWorkflow(id);
  } else if (action === "delete") {
    if (window.confirm("Delete this workflow?")) {
      await fetch(`/api/workflows/${id}`, { method: "DELETE" });
      await refreshOrchestratorUI();
    }
  }
}

async function loadWorkflow(id) {
  const res = await fetch(`/api/workflows/${id}`);
  if (!res.ok) return;
  const wf = await res.json();

  document.getElementById("workflow-id").value = wf.id;
  document.getElementById("workflow-name").value = wf.name || "";
  document.getElementById("workflow-description").value = wf.description || "";

  workflowNodes = wf.nodes || [];
  workflowEdges = wf.edges || [];
  
  // Reset node counter
  nodeIdCounter = workflowNodes.length > 0 
    ? Math.max(...workflowNodes.map(n => parseInt(n.id.replace("node_", "")) || 0)) + 1 
    : 1;

  renderWorkflowCanvas();
  selectedNodeId = null;
  hideNodeEditor();
  
  // Load run history for this workflow
  await loadWorkflowRuns(id);
}

async function loadWorkflowRuns(workflowId) {
  const runs = await fetchWorkflowRuns(workflowId);
  renderWorkflowRuns(runs);
}

function renderWorkflowRuns(runs) {
  const container = document.getElementById("workflow-runs-container");
  if (!container) return;
  container.innerHTML = "";

  if (runs.length === 0) {
    container.innerHTML = '<p class="helper-text">No runs yet</p>';
    return;
  }

  runs.slice().reverse().slice(0, 10).forEach((run) => {
    const div = document.createElement("div");
    div.className = `workflow-run-item ${run.status}`;
    const statusIcon = run.status === "completed" ? "✅" : run.status === "running" ? "⏳" : "❌";
    div.innerHTML = `
      <span>${statusIcon} Run #${run.id}</span>
      <span class="run-date">${new Date(run.started_at).toLocaleString()}</span>
      <button type="button" data-id="${run.id}">View</button>
    `;
    container.appendChild(div);
  });

  container.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      const runId = Number(e.currentTarget.getAttribute("data-id"));
      await showWorkflowRun(runId);
    });
  });
}

async function showWorkflowRun(runId) {
  const runs = await fetchWorkflowRuns();
  const run = runs.find(r => r.id === runId);
  if (!run) return;

  const view = document.getElementById("workflow-execution-view");
  const statusEl = document.getElementById("execution-status");
  const durationEl = document.getElementById("execution-duration");
  const stepsEl = document.getElementById("execution-steps");
  const outputEl = document.getElementById("execution-output");

  statusEl.textContent = `Status: ${run.status}`;
  statusEl.className = `execution-status ${run.status}`;
  
  if (run.completed_at && run.started_at) {
    const duration = new Date(run.completed_at) - new Date(run.started_at);
    durationEl.textContent = `Duration: ${duration}ms`;
  } else {
    durationEl.textContent = "";
  }

  stepsEl.innerHTML = "";
  (run.steps || []).forEach((step, idx) => {
    const stepDiv = document.createElement("div");
    stepDiv.className = `execution-step ${step.status}`;
    stepDiv.innerHTML = `
      <span class="step-num">${idx + 1}</span>
      <span class="step-node">${step.node_id}</span>
      <span class="step-status">${step.status === "completed" ? "✓" : step.status === "error" ? "✗" : "..."}</span>
      ${step.output ? `<pre class="step-output">${escapeHtml(JSON.stringify(step.output).substring(0, 200))}</pre>` : ""}
      ${step.error ? `<pre class="step-error">${escapeHtml(step.error)}</pre>` : ""}
    `;
    stepsEl.appendChild(stepDiv);
  });

  outputEl.textContent = run.final_output ? JSON.stringify(run.final_output, null, 2) : "(No output)";
  view.style.display = "block";
}

function resetWorkflowForm() {
  document.getElementById("workflow-id").value = "";
  document.getElementById("workflow-name").value = "";
  document.getElementById("workflow-description").value = "";
  workflowNodes = [];
  workflowEdges = [];
  selectedNodeId = null;
  nodeIdCounter = 1;
  renderWorkflowCanvas();
  hideNodeEditor();
  document.getElementById("workflow-message").textContent = "";
}

function addNode(type) {
  const id = `node_${nodeIdCounter++}`;
  const labels = {
    start: "Start",
    agent: "Agent Call",
    tool: "Tool Call",
    condition: "Condition",
    end: "End"
  };

  const node = {
    id: id,
    type: type,
    label: labels[type] || type,
    config: {},
    x: 50 + (workflowNodes.length % 3) * 200,
    y: 50 + Math.floor(workflowNodes.length / 3) * 120
  };

  // Default configs
  if (type === "agent") {
    node.config = { model: "", system_prompt: "", prompt_template: "{{input}}" };
  } else if (type === "tool") {
    node.config = { tool_id: "", input_template: "{{prev_output}}" };
  } else if (type === "condition") {
    node.config = { expression: "contains:yes" };
  }

  workflowNodes.push(node);
  renderWorkflowCanvas();
  selectNode(id);
}

function renderWorkflowCanvas() {
  const canvas = document.getElementById("workflow-canvas");
  if (!canvas) return;
  
  canvas.innerHTML = "";

  if (workflowNodes.length === 0) {
    canvas.innerHTML = `
      <div class="canvas-placeholder">
        <p>Click buttons above to add nodes. Drag nodes to position them. Click nodes to configure.</p>
      </div>
    `;
    return;
  }

  // Render edges first (SVG layer)
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("edges-layer");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");

  workflowEdges.forEach((edge) => {
    const fromNode = workflowNodes.find(n => n.id === edge.source);
    const toNode = workflowNodes.find(n => n.id === edge.target);
    if (!fromNode || !toNode) return;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", fromNode.x + 75);
    line.setAttribute("y1", fromNode.y + 40);
    line.setAttribute("x2", toNode.x + 75);
    line.setAttribute("y2", toNode.y + 40);
    line.classList.add("edge-line");
    if (edge.condition) {
      line.classList.add("conditional");
    }
    svg.appendChild(line);

    // Arrow head
    const angle = Math.atan2(toNode.y - fromNode.y, toNode.x - fromNode.x);
    const arrowX = toNode.x + 75 - 15 * Math.cos(angle);
    const arrowY = toNode.y + 40 - 15 * Math.sin(angle);
    
    const arrow = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    const arrowSize = 8;
    const points = [
      [arrowX, arrowY],
      [arrowX - arrowSize * Math.cos(angle - Math.PI/6), arrowY - arrowSize * Math.sin(angle - Math.PI/6)],
      [arrowX - arrowSize * Math.cos(angle + Math.PI/6), arrowY - arrowSize * Math.sin(angle + Math.PI/6)]
    ];
    arrow.setAttribute("points", points.map(p => p.join(",")).join(" "));
    arrow.classList.add("edge-arrow");
    svg.appendChild(arrow);

    // Edge label for conditions
    if (edge.condition) {
      const labelX = (fromNode.x + toNode.x) / 2 + 75;
      const labelY = (fromNode.y + toNode.y) / 2 + 40;
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", labelX);
      text.setAttribute("y", labelY - 5);
      text.classList.add("edge-label");
      text.textContent = edge.condition.substring(0, 15);
      svg.appendChild(text);
    }
  });

  canvas.appendChild(svg);

  // Render nodes
  workflowNodes.forEach((node) => {
    const nodeEl = document.createElement("div");
    nodeEl.className = `workflow-node node-${node.type}`;
    if (node.id === selectedNodeId) {
      nodeEl.classList.add("selected");
    }
    nodeEl.style.left = `${node.x}px`;
    nodeEl.style.top = `${node.y}px`;
    nodeEl.setAttribute("data-id", node.id);

    const icons = { start: "▶", agent: "🤖", tool: "🔧", condition: "❓", end: "⏹" };
    nodeEl.innerHTML = `
      <div class="node-icon">${icons[node.type] || "●"}</div>
      <div class="node-label">${node.label}</div>
    `;

    nodeEl.addEventListener("click", (e) => {
      e.stopPropagation();
      selectNode(node.id);
    });

    // Make draggable
    nodeEl.addEventListener("mousedown", (e) => {
      if (e.target.classList.contains("workflow-node") || e.target.parentElement.classList.contains("workflow-node")) {
        startDrag(e, node);
      }
    });

    canvas.appendChild(nodeEl);
  });

  // Click on canvas deselects
  canvas.addEventListener("click", (e) => {
    if (e.target === canvas || e.target.classList.contains("canvas-placeholder")) {
      selectedNodeId = null;
      hideNodeEditor();
      renderWorkflowCanvas();
    }
  });
}

let isDragging = false;
let dragNode = null;
let dragOffset = { x: 0, y: 0 };

function startDrag(e, node) {
  isDragging = true;
  dragNode = node;
  dragOffset = {
    x: e.clientX - node.x,
    y: e.clientY - node.y
  };
  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", endDrag);
}

function onDrag(e) {
  if (!isDragging || !dragNode) return;
  
  const canvas = document.getElementById("workflow-canvas");
  const rect = canvas.getBoundingClientRect();
  
  dragNode.x = Math.max(0, Math.min(e.clientX - dragOffset.x, rect.width - 150));
  dragNode.y = Math.max(0, Math.min(e.clientY - dragOffset.y, rect.height - 80));
  
  renderWorkflowCanvas();
}

function endDrag() {
  isDragging = false;
  dragNode = null;
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", endDrag);
}

function selectNode(nodeId) {
  selectedNodeId = nodeId;
  renderWorkflowCanvas();
  showNodeEditor(nodeId);
}

function showNodeEditor(nodeId) {
  const node = workflowNodes.find(n => n.id === nodeId);
  if (!node) return;

  const editor = document.getElementById("node-editor");
  editor.style.display = "block";

  document.getElementById("node-config-id").value = node.id;
  document.getElementById("node-config-label").value = node.label;

  // Type-specific fields
  const fieldsContainer = document.getElementById("node-config-type-fields");
  fieldsContainer.innerHTML = "";

  if (node.type === "agent") {
    fieldsContainer.innerHTML = `
      <label>
        Model
        <input type="text" id="node-cfg-model" value="${node.config.model || ""}" placeholder="Model name (optional)" />
      </label>
      <label>
        System Prompt
        <textarea id="node-cfg-system" rows="2">${node.config.system_prompt || ""}</textarea>
      </label>
      <label>
        Prompt Template
        <textarea id="node-cfg-prompt" rows="2" placeholder="Use {{input}} or {{prev_output}}">${node.config.prompt_template || "{{input}}"}</textarea>
      </label>
    `;
  } else if (node.type === "tool") {
    fieldsContainer.innerHTML = `
      <label>
        Tool ID
        <input type="text" id="node-cfg-tool-id" value="${node.config.tool_id || ""}" placeholder="Tool ID" />
      </label>
      <label>
        Input Template
        <textarea id="node-cfg-tool-input" rows="2" placeholder="Use {{prev_output}}">${node.config.input_template || "{{prev_output}}"}</textarea>
      </label>
    `;
  } else if (node.type === "condition") {
    fieldsContainer.innerHTML = `
      <label>
        Expression
        <input type="text" id="node-cfg-condition" value="${node.config.expression || ""}" placeholder="contains:yes, equals:approved, >:50" />
      </label>
      <p class="helper-text">Operators: contains, equals, startswith, endswith, >, <, >=, <=</p>
    `;
  }

  // Populate edge targets
  updateEdgeTargetSelect();
  updateCurrentEdgesList();
  
  // Show/hide condition input based on node type
  const conditionWrap = document.getElementById("node-connect-condition-wrap");
  conditionWrap.style.display = node.type === "condition" ? "block" : "none";
}

function hideNodeEditor() {
  document.getElementById("node-editor").style.display = "none";
}

function updateEdgeTargetSelect() {
  const select = document.getElementById("node-connect-target");
  select.innerHTML = '<option value="">-- Select target node --</option>';
  
  workflowNodes.forEach((node) => {
    if (node.id !== selectedNodeId) {
      const opt = document.createElement("option");
      opt.value = node.id;
      opt.textContent = `${node.label} (${node.id})`;
      select.appendChild(opt);
    }
  });
}

function updateCurrentEdgesList() {
  const list = document.getElementById("node-edges-list");
  list.innerHTML = "";
  
  const nodeEdges = workflowEdges.filter(e => e.source === selectedNodeId);
  
  if (nodeEdges.length === 0) {
    list.innerHTML = "<li>No connections</li>";
    return;
  }
  
  nodeEdges.forEach((edge, idx) => {
    const targetNode = workflowNodes.find(n => n.id === edge.target);
    const li = document.createElement("li");
    li.innerHTML = `
      → ${targetNode ? targetNode.label : edge.target} 
      ${edge.condition ? `<span class="edge-condition-tag">(${edge.condition})</span>` : ""}
      <button type="button" class="remove-edge-btn" data-idx="${idx}">✕</button>
    `;
    list.appendChild(li);
  });
  
  list.querySelectorAll(".remove-edge-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const idx = Number(e.currentTarget.getAttribute("data-idx"));
      const nodeEdges = workflowEdges.filter(ed => ed.source === selectedNodeId);
      const edgeToRemove = nodeEdges[idx];
      workflowEdges = workflowEdges.filter(ed => ed !== edgeToRemove);
      updateCurrentEdgesList();
      renderWorkflowCanvas();
    });
  });
}

function addEdge() {
  const targetId = document.getElementById("node-connect-target").value;
  if (!targetId || !selectedNodeId) return;
  
  const condition = document.getElementById("node-connect-condition").value.trim() || null;
  
  // Check for duplicate
  const exists = workflowEdges.some(e => e.source === selectedNodeId && e.target === targetId);
  if (exists) {
    alert("Edge already exists");
    return;
  }
  
  workflowEdges.push({
    source: selectedNodeId,
    target: targetId,
    condition: condition
  });
  
  document.getElementById("node-connect-target").value = "";
  document.getElementById("node-connect-condition").value = "";
  
  updateCurrentEdgesList();
  renderWorkflowCanvas();
}

function updateNodeFromEditor() {
  const node = workflowNodes.find(n => n.id === selectedNodeId);
  if (!node) return;
  
  node.label = document.getElementById("node-config-label").value;
  
  if (node.type === "agent") {
    node.config.model = document.getElementById("node-cfg-model")?.value || "";
    node.config.system_prompt = document.getElementById("node-cfg-system")?.value || "";
    node.config.prompt_template = document.getElementById("node-cfg-prompt")?.value || "{{input}}";
  } else if (node.type === "tool") {
    node.config.tool_id = document.getElementById("node-cfg-tool-id")?.value || "";
    node.config.input_template = document.getElementById("node-cfg-tool-input")?.value || "{{prev_output}}";
  } else if (node.type === "condition") {
    node.config.expression = document.getElementById("node-cfg-condition")?.value || "";
  }
  
  renderWorkflowCanvas();
  document.getElementById("workflow-message").textContent = "Node updated";
  setTimeout(() => { document.getElementById("workflow-message").textContent = ""; }, 2000);
}

function deleteSelectedNode() {
  if (!selectedNodeId) return;
  if (!confirm("Delete this node?")) return;
  
  workflowNodes = workflowNodes.filter(n => n.id !== selectedNodeId);
  workflowEdges = workflowEdges.filter(e => e.source !== selectedNodeId && e.target !== selectedNodeId);
  
  selectedNodeId = null;
  hideNodeEditor();
  renderWorkflowCanvas();
}

async function saveWorkflow() {
  const messageEl = document.getElementById("workflow-message");
  messageEl.textContent = "";
  
  const id = document.getElementById("workflow-id").value;
  const name = document.getElementById("workflow-name").value.trim();
  const description = document.getElementById("workflow-description").value.trim();
  
  if (!name) {
    messageEl.textContent = "Name is required";
    return;
  }
  
  if (workflowNodes.length === 0) {
    messageEl.textContent = "Add at least one node";
    return;
  }
  
  const payload = {
    name,
    description,
    nodes: workflowNodes,
    edges: workflowEdges
  };
  
  const isUpdate = !!id;
  const url = isUpdate ? `/api/workflows/${id}` : "/api/workflows";
  const method = isUpdate ? "PUT" : "POST";
  
  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      messageEl.textContent = `Save failed: ${res.status}`;
      return;
    }
    
    const saved = await res.json();
    document.getElementById("workflow-id").value = saved.id;
    messageEl.textContent = "Workflow saved!";
    messageEl.style.color = "#4ade80";
    
    await refreshOrchestratorUI();
  } catch (err) {
    messageEl.textContent = `Error: ${err.message}`;
  }
}

async function runWorkflow() {
  const messageEl = document.getElementById("workflow-run-message");
  messageEl.textContent = "";
  
  const workflowId = document.getElementById("workflow-id").value;
  if (!workflowId) {
    messageEl.textContent = "Save the workflow first";
    return;
  }
  
  const inputStr = document.getElementById("workflow-run-input").value.trim();
  let inputData = {};
  
  if (inputStr) {
    try {
      inputData = JSON.parse(inputStr);
    } catch (e) {
      messageEl.textContent = "Invalid JSON input";
      return;
    }
  }
  
  messageEl.textContent = "Running...";
  
  try {
    const res = await fetch(`/api/workflows/${workflowId}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ workflow_id: Number(workflowId), input_data: inputData })
    });
    
    if (!res.ok) {
      const errData = await res.json();
      messageEl.textContent = `Run failed: ${errData.detail || res.status}`;
      return;
    }
    
    const run = await res.json();
    messageEl.textContent = "Complete!";
    
    // Show execution result
    await showWorkflowRun(run.id);
    await loadWorkflowRuns(Number(workflowId));
  } catch (err) {
    messageEl.textContent = `Error: ${err.message}`;
  }
}

function clearWorkflowCanvas() {
  if (workflowNodes.length > 0 && !confirm("Clear all nodes and edges?")) return;
  workflowNodes = [];
  workflowEdges = [];
  selectedNodeId = null;
  nodeIdCounter = 1;
  hideNodeEditor();
  renderWorkflowCanvas();
}

async function refreshOrchestratorUI() {
  const workflows = await fetchWorkflows();
  renderWorkflowsTable(workflows);
  
  const runs = await fetchWorkflowRuns();
  renderWorkflowRuns(runs);
}

function initOrchestratorUI() {
  const newBtn = document.getElementById("workflow-new-btn");
  const saveBtn = document.getElementById("workflow-save-btn");
  const resetBtn = document.getElementById("workflow-reset-btn");
  const clearCanvasBtn = document.getElementById("workflow-clear-canvas");
  const runBtn = document.getElementById("workflow-run-btn");
  const addEdgeBtn = document.getElementById("node-add-edge-btn");
  const nodeSaveBtn = document.getElementById("node-save-btn");
  const nodeDeleteBtn = document.getElementById("node-delete-btn");
  const executionCloseBtn = document.getElementById("execution-close-btn");
  
  if (!newBtn) return;
  
  newBtn.addEventListener("click", resetWorkflowForm);
  saveBtn.addEventListener("click", saveWorkflow);
  resetBtn.addEventListener("click", resetWorkflowForm);
  clearCanvasBtn.addEventListener("click", clearWorkflowCanvas);
  runBtn.addEventListener("click", runWorkflow);
  addEdgeBtn.addEventListener("click", addEdge);
  nodeSaveBtn.addEventListener("click", updateNodeFromEditor);
  nodeDeleteBtn.addEventListener("click", deleteSelectedNode);
  executionCloseBtn.addEventListener("click", () => {
    document.getElementById("workflow-execution-view").style.display = "none";
  });
  
  // Node add buttons
  document.querySelectorAll(".node-add-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const type = btn.getAttribute("data-type");
      addNode(type);
    });
  });
  
  refreshOrchestratorUI().catch((err) => {
    console.error("Failed to load orchestrator data:", err);
  });
}

// ========== Chat Lab (Multi-Turn Branching Conversations) ==========

let currentChatTreeId = null;
let branchFromNodeId = null;

async function fetchChatTrees() {
  const res = await fetch("/api/chat-lab/trees");
  if (!res.ok) throw new Error(`Failed to fetch chat trees: ${res.status}`);
  const data = await res.json();
  return data.trees || [];
}

async function fetchChatTree(treeId) {
  const res = await fetch(`/api/chat-lab/trees/${treeId}`);
  if (!res.ok) throw new Error(`Failed to fetch chat tree: ${res.status}`);
  return res.json();
}

async function fetchChatTreeStructure(treeId) {
  const res = await fetch(`/api/chat-lab/trees/${treeId}/structure`);
  if (!res.ok) return null;
  return res.json();
}

async function fetchChatHistory(treeId, nodeId = null) {
  let url = `/api/chat-lab/trees/${treeId}/history`;
  if (nodeId) url += `?node_id=${encodeURIComponent(nodeId)}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const data = await res.json();
  return data.messages || [];
}

function renderChatTreesTable(trees) {
  const tbody = document.querySelector("#chat-trees-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (trees.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="color:#6b7280;text-align:center;">No conversations yet</td></tr>';
    return;
  }

  trees.forEach((tree) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${tree.id}</td>
      <td>${escapeHtml(tree.name)}</td>
      <td>
        <button type="button" data-action="load" data-id="${tree.id}">Open</button>
        <button type="button" data-action="edit" data-id="${tree.id}">Edit</button>
        <button type="button" data-action="delete" data-id="${tree.id}">✕</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", onChatTreeAction);
  });
}

async function onChatTreeAction(event) {
  const btn = event.currentTarget;
  const id = Number(btn.dataset.id);
  const action = btn.dataset.action;

  if (action === "load") {
    await loadChatTree(id);
  } else if (action === "edit") {
    await populateChatTreeForm(id);
  } else if (action === "delete") {
    if (confirm("Delete this conversation and all its messages?")) {
      await fetch(`/api/chat-lab/trees/${id}`, { method: "DELETE" });
      if (currentChatTreeId === id) {
        currentChatTreeId = null;
        renderChatMessages([]);
        renderChatTreeVisualization(null);
      }
      await refreshChatTreesUI();
    }
  }
}

async function loadChatTree(treeId) {
  currentChatTreeId = treeId;
  branchFromNodeId = null;
  document.getElementById("chat-branch-indicator").style.display = "none";
  
  const tree = await fetchChatTree(treeId);
  const history = await fetchChatHistory(treeId);
  
  renderChatMessages(history, tree);
  
  // Update tree form to show current settings
  document.getElementById("chat-tree-id").value = tree.id;
  document.getElementById("chat-tree-name").value = tree.name || "";
  document.getElementById("chat-tree-model").value = tree.model_name || "";
  document.getElementById("chat-tree-system").value = tree.system_prompt || "";
  document.getElementById("chat-tree-description").value = tree.description || "";
  
  // Refresh tree visualization
  await refreshChatTreeVisualization();
}

function renderChatMessages(messages, tree = null) {
  const container = document.getElementById("chat-lab-messages");
  if (!container) return;
  
  if (!messages || messages.length === 0) {
    container.innerHTML = `
      <div class="chat-empty-state">
        ${currentChatTreeId 
          ? "<p>Start the conversation by sending a message below.</p>"
          : "<p>Select a conversation or create a new one to start chatting.</p>"}
      </div>
    `;
    return;
  }

  container.innerHTML = "";
  
  messages.forEach((msg, idx) => {
    const div = document.createElement("div");
    div.className = `chat-message ${msg.role}`;
    div.dataset.nodeId = msg.id || `msg-${idx}`;
    
    let metaHtml = "";
    if (msg.metadata) {
      const parts = [];
      if (msg.metadata.latency_ms) parts.push(`${msg.metadata.latency_ms.toFixed(0)}ms`);
      if (msg.metadata.total_tokens) parts.push(`${msg.metadata.total_tokens} tokens`);
      if (msg.metadata.model) parts.push(msg.metadata.model);
      if (parts.length > 0) metaHtml = `<div class="chat-message-meta">${parts.join(" • ")}</div>`;
    }
    
    div.innerHTML = `
      <div class="chat-message-content">${escapeHtml(msg.content)}</div>
      ${metaHtml}
      <div class="chat-message-actions">
        <button type="button" data-action="branch" title="Create branch from here">🌿</button>
        <button type="button" data-action="copy" title="Copy text">📋</button>
      </div>
    `;
    container.appendChild(div);
  });

  // Add action handlers
  container.querySelectorAll(".chat-message-actions button").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const msgDiv = btn.closest(".chat-message");
      const nodeId = msgDiv.dataset.nodeId;
      const action = btn.dataset.action;
      
      if (action === "branch") {
        startBranching(nodeId);
      } else if (action === "copy") {
        const text = msgDiv.querySelector(".chat-message-content").textContent;
        navigator.clipboard.writeText(text);
      }
    });
  });

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

function startBranching(fromNodeId) {
  branchFromNodeId = fromNodeId;
  document.getElementById("chat-branch-indicator").style.display = "flex";
  document.getElementById("chat-branch-info").textContent = `Branch will be created after message ${fromNodeId}`;
}

function cancelBranching() {
  branchFromNodeId = null;
  document.getElementById("chat-branch-indicator").style.display = "none";
}

async function sendChatMessage() {
  if (!currentChatTreeId) {
    document.getElementById("chat-tree-message").textContent = "Please select or create a conversation first.";
    return;
  }
  
  const input = document.getElementById("chat-lab-input");
  const content = input.value.trim();
  if (!content) return;
  
  const sendBtn = document.getElementById("chat-lab-send-btn");
  sendBtn.disabled = true;
  sendBtn.textContent = "Sending...";
  
  try {
    const payload = { content };
    
    // If branching, include the parent node
    if (branchFromNodeId) {
      // First create the branch
      await fetch(`/api/chat-lab/trees/${currentChatTreeId}/branch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_node_id: branchFromNodeId })
      });
      payload.parent_node_id = branchFromNodeId;
      cancelBranching();
    }
    
    const res = await fetch(`/api/chat-lab/trees/${currentChatTreeId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
    if (data.error) {
      document.getElementById("chat-tree-message").textContent = `Error: ${data.error}`;
    } else {
      input.value = "";
      // Reload conversation
      await loadChatTree(currentChatTreeId);
    }
  } catch (err) {
    document.getElementById("chat-tree-message").textContent = `Error: ${err.message}`;
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
  }
}

async function refreshChatTreeVisualization() {
  if (!currentChatTreeId) {
    renderChatTreeVisualization(null);
    return;
  }
  
  const structure = await fetchChatTreeStructure(currentChatTreeId);
  renderChatTreeVisualization(structure);
}

function renderChatTreeVisualization(structure) {
  const container = document.getElementById("chat-tree-visualization");
  if (!container) return;
  
  if (!structure || !structure.id) {
    container.innerHTML = '<div class="tree-empty-state">No conversation loaded</div>';
    return;
  }
  
  container.innerHTML = "";
  
  function renderNode(node, isRoot = false) {
    const nodeDiv = document.createElement("div");
    nodeDiv.className = "tree-node";
    if (isRoot) nodeDiv.style.marginLeft = "0";
    
    const contentDiv = document.createElement("div");
    contentDiv.className = "tree-node-content" + (node.is_active ? " active" : "");
    contentDiv.dataset.nodeId = node.id;
    
    contentDiv.innerHTML = `
      <span class="tree-node-role ${node.role}">${node.role.charAt(0).toUpperCase()}</span>
      <span class="tree-node-preview">${escapeHtml(node.content_preview)}</span>
      ${node.branch_name ? `<span class="tree-node-branch">${escapeHtml(node.branch_name)}</span>` : ""}
    `;
    
    contentDiv.addEventListener("click", () => switchToNode(node.id));
    nodeDiv.appendChild(contentDiv);
    
    if (node.children && node.children.length > 0) {
      const childrenDiv = document.createElement("div");
      childrenDiv.className = "tree-children";
      node.children.forEach((child) => {
        childrenDiv.appendChild(renderNode(child, false));
      });
      nodeDiv.appendChild(childrenDiv);
    }
    
    return nodeDiv;
  }
  
  container.appendChild(renderNode(structure, true));
}

async function switchToNode(nodeId) {
  if (!currentChatTreeId) return;
  
  await fetch(`/api/chat-lab/trees/${currentChatTreeId}/switch?to_node_id=${encodeURIComponent(nodeId)}`, {
    method: "POST"
  });
  
  await loadChatTree(currentChatTreeId);
}

async function populateChatTreeForm(treeId) {
  const tree = await fetchChatTree(treeId);
  document.getElementById("chat-tree-id").value = tree.id;
  document.getElementById("chat-tree-name").value = tree.name || "";
  document.getElementById("chat-tree-model").value = tree.model_name || "";
  document.getElementById("chat-tree-system").value = tree.system_prompt || "";
  document.getElementById("chat-tree-description").value = tree.description || "";
}

function resetChatTreeForm() {
  document.getElementById("chat-tree-id").value = "";
  document.getElementById("chat-tree-name").value = "";
  document.getElementById("chat-tree-model").value = "";
  document.getElementById("chat-tree-system").value = "";
  document.getElementById("chat-tree-description").value = "";
  document.getElementById("chat-tree-message").textContent = "";
}

async function submitChatTreeForm(event) {
  event.preventDefault();
  const messageEl = document.getElementById("chat-tree-message");
  messageEl.textContent = "";
  
  const id = document.getElementById("chat-tree-id").value;
  const name = document.getElementById("chat-tree-name").value.trim();
  const model_name = document.getElementById("chat-tree-model").value;
  const system_prompt = document.getElementById("chat-tree-system").value;
  const description = document.getElementById("chat-tree-description").value;
  
  if (!name) {
    messageEl.textContent = "Name is required";
    return;
  }
  
  const payload = { name, model_name, system_prompt, description };
  const isUpdate = !!id;
  const url = isUpdate ? `/api/chat-lab/trees/${id}` : "/api/chat-lab/trees";
  const method = isUpdate ? "PUT" : "POST";
  
  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      messageEl.textContent = `Save failed: ${res.status}`;
      return;
    }
    
    const tree = await res.json();
    messageEl.textContent = "Saved";
    await refreshChatTreesUI();
    
    // If new tree, load it
    if (!isUpdate) {
      await loadChatTree(tree.id);
    }
  } catch (err) {
    messageEl.textContent = `Error: ${err.message}`;
  }
}

async function refreshChatTreesUI() {
  const trees = await fetchChatTrees();
  renderChatTreesTable(trees);
}

function initChatLabUI() {
  const form = document.getElementById("chat-tree-form");
  const newBtn = document.getElementById("chat-tree-new-btn");
  const resetBtn = document.getElementById("chat-tree-reset-btn");
  const sendBtn = document.getElementById("chat-lab-send-btn");
  const refreshTreeBtn = document.getElementById("chat-refresh-tree-btn");
  const cancelBranchBtn = document.getElementById("chat-cancel-branch-btn");
  const inputEl = document.getElementById("chat-lab-input");
  
  if (!form) return;
  
  form.addEventListener("submit", submitChatTreeForm);
  newBtn.addEventListener("click", resetChatTreeForm);
  resetBtn.addEventListener("click", resetChatTreeForm);
  sendBtn.addEventListener("click", sendChatMessage);
  refreshTreeBtn.addEventListener("click", refreshChatTreeVisualization);
  cancelBranchBtn.addEventListener("click", cancelBranching);
  
  // Shift+Enter sends, Enter adds newline
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });
  
  refreshChatTreesUI().catch((err) => {
    console.error("Failed to load chat trees:", err);
  });
}


// ========== Guardrail Tester ==========

function initGuardrailsUI() {
  const newRuleBtn = document.getElementById("guardrail-new-rule-btn");
  const newTestBtn = document.getElementById("guardrail-new-test-btn");
  const checkBtn = document.getElementById("guardrail-check-btn");
  const runAllBtn = document.getElementById("guardrail-run-all-btn");
  
  const ruleForm = document.getElementById("guardrail-rule-form");
  const testForm = document.getElementById("guardrail-test-form");
  
  const ruleCancelBtn = document.getElementById("guardrail-rule-cancel");
  const ruleDeleteBtn = document.getElementById("guardrail-rule-delete");
  const testCancelBtn = document.getElementById("guardrail-test-cancel");
  const testDeleteBtn = document.getElementById("guardrail-test-delete");
  
  if (!newRuleBtn) return;
  
  newRuleBtn.addEventListener("click", () => showRuleEditor(null));
  newTestBtn.addEventListener("click", () => showTestEditor(null));
  checkBtn.addEventListener("click", checkGuardrails);
  runAllBtn.addEventListener("click", runGuardrailTests);
  
  ruleForm.addEventListener("submit", saveGuardrailRule);
  testForm.addEventListener("submit", saveGuardrailTest);
  
  ruleCancelBtn.addEventListener("click", hideEditors);
  ruleDeleteBtn.addEventListener("click", deleteGuardrailRule);
  testCancelBtn.addEventListener("click", hideEditors);
  testDeleteBtn.addEventListener("click", deleteGuardrailTest);
  
  // Refresh on tab select
  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.getAttribute("data-tab") === "guardrails-tab") {
        refreshGuardrailsUI();
      }
    });
  });
  
  refreshGuardrailsUI();
}

async function refreshGuardrailsUI() {
  try {
    const [rulesRes, testsRes] = await Promise.all([
      fetch("/api/guardrails/rules"),
      fetch("/api/guardrails/tests")
    ]);
    
    const rulesData = await rulesRes.json();
    const testsData = await testsRes.json();
    
    renderGuardrailRules(rulesData.rules || []);
    renderGuardrailTests(testsData.tests || []);
  } catch (err) {
    console.error("Failed to load guardrails data:", err);
  }
}

function renderGuardrailRules(rules) {
  const tbody = document.querySelector("#guardrails-rules-table tbody");
  if (!tbody) return;
  
  tbody.innerHTML = rules.map(rule => `
    <tr>
      <td>
        <input type="checkbox" ${rule.enabled ? "checked" : ""} 
               onchange="toggleGuardrailRule(${rule.id})" />
      </td>
      <td title="${rule.description}">${rule.name}</td>
      <td><span class="rule-type-badge ${rule.type}">${rule.type}</span></td>
      <td>
        <button onclick="editGuardrailRule(${rule.id})">✏️</button>
      </td>
    </tr>
  `).join("");
}

function renderGuardrailTests(tests) {
  const tbody = document.querySelector("#guardrails-tests-table tbody");
  if (!tbody) return;
  
  tbody.innerHTML = tests.map(test => `
    <tr>
      <td title="${test.description || test.input_text}">${test.name}</td>
      <td>${test.expected_blocked ? "🚫 Block" : "✅ Pass"}</td>
      <td>
        <button onclick="editGuardrailTest(${test.id})">✏️</button>
      </td>
    </tr>
  `).join("");
}

function hideEditors() {
  document.getElementById("guardrail-rule-editor").style.display = "none";
  document.getElementById("guardrail-test-editor").style.display = "none";
  document.getElementById("guardrail-editor-placeholder").style.display = "block";
}

function showRuleEditor(rule) {
  hideEditors();
  document.getElementById("guardrail-editor-placeholder").style.display = "none";
  document.getElementById("guardrail-rule-editor").style.display = "block";
  
  const form = document.getElementById("guardrail-rule-form");
  if (rule) {
    document.getElementById("guardrail-rule-id").value = rule.id;
    document.getElementById("guardrail-rule-name").value = rule.name;
    document.getElementById("guardrail-rule-description").value = rule.description || "";
    document.getElementById("guardrail-rule-type").value = rule.type;
    document.getElementById("guardrail-rule-config").value = JSON.stringify(rule.config, null, 2);
    document.getElementById("guardrail-rule-enabled").checked = rule.enabled;
    document.getElementById("guardrail-rule-delete").style.display = "inline-block";
  } else {
    form.reset();
    document.getElementById("guardrail-rule-id").value = "";
    document.getElementById("guardrail-rule-config").value = '{\n  "mode": "warn"\n}';
    document.getElementById("guardrail-rule-delete").style.display = "none";
  }
}

function showTestEditor(test) {
  hideEditors();
  document.getElementById("guardrail-editor-placeholder").style.display = "none";
  document.getElementById("guardrail-test-editor").style.display = "block";
  
  const form = document.getElementById("guardrail-test-form");
  if (test) {
    document.getElementById("guardrail-test-id").value = test.id;
    document.getElementById("guardrail-test-name").value = test.name;
    document.getElementById("guardrail-test-description").value = test.description || "";
    document.getElementById("guardrail-test-input").value = test.input_text;
    document.getElementById("guardrail-test-blocked").checked = test.expected_blocked;
    document.getElementById("guardrail-test-flags").value = (test.expected_flags || []).join(", ");
    document.getElementById("guardrail-test-tags").value = (test.tags || []).join(", ");
    document.getElementById("guardrail-test-delete").style.display = "inline-block";
  } else {
    form.reset();
    document.getElementById("guardrail-test-id").value = "";
    document.getElementById("guardrail-test-delete").style.display = "none";
  }
}

async function editGuardrailRule(ruleId) {
  try {
    const res = await fetch(`/api/guardrails/rules/${ruleId}`);
    const rule = await res.json();
    showRuleEditor(rule);
  } catch (err) {
    console.error("Failed to load rule:", err);
  }
}

async function editGuardrailTest(testId) {
  try {
    const res = await fetch(`/api/guardrails/tests/${testId}`);
    const test = await res.json();
    showTestEditor(test);
  } catch (err) {
    console.error("Failed to load test:", err);
  }
}

async function toggleGuardrailRule(ruleId) {
  try {
    await fetch(`/api/guardrails/rules/${ruleId}/toggle`, { method: "POST" });
    refreshGuardrailsUI();
  } catch (err) {
    console.error("Failed to toggle rule:", err);
  }
}

async function saveGuardrailRule(e) {
  e.preventDefault();
  
  const ruleId = document.getElementById("guardrail-rule-id").value;
  let config = {};
  try {
    config = JSON.parse(document.getElementById("guardrail-rule-config").value || "{}");
  } catch (err) {
    alert("Invalid JSON in configuration");
    return;
  }
  
  const payload = {
    name: document.getElementById("guardrail-rule-name").value,
    description: document.getElementById("guardrail-rule-description").value,
    type: document.getElementById("guardrail-rule-type").value,
    config: config,
    enabled: document.getElementById("guardrail-rule-enabled").checked,
  };
  
  try {
    const url = ruleId ? `/api/guardrails/rules/${ruleId}` : "/api/guardrails/rules";
    const method = ruleId ? "PUT" : "POST";
    
    await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    hideEditors();
    refreshGuardrailsUI();
  } catch (err) {
    console.error("Failed to save rule:", err);
  }
}

async function deleteGuardrailRule() {
  const ruleId = document.getElementById("guardrail-rule-id").value;
  if (!ruleId || !confirm("Delete this rule?")) return;
  
  try {
    await fetch(`/api/guardrails/rules/${ruleId}`, { method: "DELETE" });
    hideEditors();
    refreshGuardrailsUI();
  } catch (err) {
    console.error("Failed to delete rule:", err);
  }
}

async function saveGuardrailTest(e) {
  e.preventDefault();
  
  const testId = document.getElementById("guardrail-test-id").value;
  const flagsStr = document.getElementById("guardrail-test-flags").value;
  const tagsStr = document.getElementById("guardrail-test-tags").value;
  
  const payload = {
    name: document.getElementById("guardrail-test-name").value,
    description: document.getElementById("guardrail-test-description").value,
    input_text: document.getElementById("guardrail-test-input").value,
    expected_blocked: document.getElementById("guardrail-test-blocked").checked,
    expected_flags: flagsStr ? flagsStr.split(",").map(s => s.trim()).filter(Boolean) : [],
    tags: tagsStr ? tagsStr.split(",").map(s => s.trim()).filter(Boolean) : [],
  };
  
  try {
    const url = testId ? `/api/guardrails/tests/${testId}` : "/api/guardrails/tests";
    const method = testId ? "PUT" : "POST";
    
    await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    hideEditors();
    refreshGuardrailsUI();
  } catch (err) {
    console.error("Failed to save test:", err);
  }
}

async function deleteGuardrailTest() {
  const testId = document.getElementById("guardrail-test-id").value;
  if (!testId || !confirm("Delete this test case?")) return;
  
  try {
    await fetch(`/api/guardrails/tests/${testId}`, { method: "DELETE" });
    hideEditors();
    refreshGuardrailsUI();
  } catch (err) {
    console.error("Failed to delete test:", err);
  }
}

async function checkGuardrails() {
  const text = document.getElementById("guardrail-check-input").value.trim();
  if (!text) {
    alert("Please enter text to check");
    return;
  }
  
  const resultEl = document.getElementById("guardrail-check-result");
  const statusEl = document.getElementById("guardrail-check-status");
  const timeEl = document.getElementById("guardrail-check-time");
  const flagsEl = document.getElementById("guardrail-check-flags");
  const passedEl = document.getElementById("guardrail-check-passed");
  
  try {
    const res = await fetch("/api/guardrails/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    
    const result = await res.json();
    
    resultEl.style.display = "block";
    
    // Status badge
    if (result.blocked) {
      statusEl.textContent = "🚫 BLOCKED";
      statusEl.className = "status-badge blocked";
    } else if (result.flags && result.flags.length > 0) {
      statusEl.textContent = "⚠️ FLAGGED";
      statusEl.className = "status-badge flagged";
    } else {
      statusEl.textContent = "✅ PASSED";
      statusEl.className = "status-badge passed";
    }
    
    timeEl.textContent = `${result.execution_time_ms.toFixed(2)}ms`;
    
    // Flags
    if (result.flags && result.flags.length > 0) {
      flagsEl.innerHTML = `
        <h4>Flags Triggered:</h4>
        ${result.flags.map(f => `
          <div class="flag-item ${f.severity}">
            <div>
              <span class="flag-rule">${f.rule_name}</span>
              <span class="rule-type-badge ${f.type}">${f.type}</span>
            </div>
            <div class="flag-matches">
              ${f.matches.map(m => JSON.stringify(m)).join(", ")}
            </div>
          </div>
        `).join("")}
      `;
    } else {
      flagsEl.innerHTML = "";
    }
    
    // Passed rules
    if (result.passed_rules && result.passed_rules.length > 0) {
      passedEl.innerHTML = `<h4>Passed Rules:</h4> ${result.passed_rules.join(", ")}`;
    } else {
      passedEl.innerHTML = "";
    }
    
  } catch (err) {
    console.error("Failed to check guardrails:", err);
    resultEl.style.display = "block";
    statusEl.textContent = "❌ ERROR";
    statusEl.className = "status-badge blocked";
    flagsEl.innerHTML = `<div class="flag-item block">${err.message}</div>`;
  }
}

async function runGuardrailTests() {
  const summaryEl = document.getElementById("guardrail-test-summary");
  const resultsEl = document.getElementById("guardrail-test-results");
  
  try {
    const res = await fetch("/api/guardrails/run-tests", { method: "POST" });
    const data = await res.json();
    
    summaryEl.style.display = "block";
    
    document.getElementById("guardrail-test-total").textContent = `Total: ${data.total}`;
    document.getElementById("guardrail-test-passed").textContent = `Passed: ${data.passed}`;
    document.getElementById("guardrail-test-failed").textContent = `Failed: ${data.failed}`;
    document.getElementById("guardrail-test-rate").textContent = `Rate: ${data.pass_rate.toFixed(1)}%`;
    
    resultsEl.innerHTML = data.results.map(r => `
      <div class="test-result-item ${r.passed ? "passed" : "failed"}">
        <span class="test-result-icon">${r.passed ? "✅" : "❌"}</span>
        <span class="test-result-name">${r.test_name}</span>
        <span class="test-result-details">
          ${r.passed ? "" : (r.block_match ? "" : "Block mismatch. ") + (r.flags_match ? "" : "Flags mismatch.")}
        </span>
      </div>
    `).join("");
    
  } catch (err) {
    console.error("Failed to run tests:", err);
    resultsEl.innerHTML = `<div class="test-result-item failed">Error: ${err.message}</div>`;
  }
}

// ========== History & Replay ==========

let historyPage = 0;
const historyPageSize = 20;
let selectedHistoryEntryId = null;

async function fetchHistory(filters = {}) {
  let url = `/api/history?limit=${historyPageSize}&offset=${historyPage * historyPageSize}`;
  
  if (filters.endpoint) url += `&endpoint=${encodeURIComponent(filters.endpoint)}`;
  if (filters.model) url += `&model=${encodeURIComponent(filters.model)}`;
  if (filters.success !== undefined && filters.success !== "") url += `&success=${filters.success}`;
  if (filters.starred !== undefined && filters.starred !== "") url += `&starred=${filters.starred}`;
  if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
  
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch history: ${res.status}`);
  const data = await res.json();
  return data.entries || [];
}

async function fetchHistoryStats() {
  const res = await fetch("/api/history/stats");
  if (!res.ok) return null;
  return res.json();
}

async function fetchHistoryEndpoints() {
  const res = await fetch("/api/history/endpoints");
  if (!res.ok) return [];
  const data = await res.json();
  return data.endpoints || [];
}

async function fetchHistoryModels() {
  const res = await fetch("/api/history/models");
  if (!res.ok) return [];
  const data = await res.json();
  return data.models || [];
}

function formatTimestamp(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

function formatTimeAgo(ts) {
  const now = Date.now() / 1000;
  const diff = now - ts;
  
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function getEndpointIcon(endpoint) {
  const icons = {
    generate: "✏️",
    chat: "💬",
    ab_test: "⚖️",
    chat_lab: "🔬",
    workflow: "🔄",
    bulk: "📦",
    replay: "🔁"
  };
  return icons[endpoint] || "📝";
}

function renderHistoryStats(stats) {
  if (!stats) return;
  
  document.getElementById("history-stat-total").textContent = stats.total_entries || 0;
  document.getElementById("history-stat-success").textContent = 
    `${(stats.success_rate || 0).toFixed(1)}%`;
  document.getElementById("history-stat-latency").textContent = 
    `${(stats.avg_latency_ms || 0).toFixed(0)}ms`;
  document.getElementById("history-stat-tokens").textContent = 
    (stats.total_tokens || 0).toLocaleString();
  document.getElementById("history-stat-starred").textContent = stats.starred_count || 0;
}

async function populateHistoryFilters() {
  const endpoints = await fetchHistoryEndpoints();
  const models = await fetchHistoryModels();
  
  const endpointSelect = document.getElementById("history-filter-endpoint");
  const modelSelect = document.getElementById("history-filter-model");
  
  // Clear existing options except first
  while (endpointSelect.options.length > 1) endpointSelect.remove(1);
  while (modelSelect.options.length > 1) modelSelect.remove(1);
  
  endpoints.forEach(e => {
    const opt = document.createElement("option");
    opt.value = e;
    opt.textContent = e;
    endpointSelect.appendChild(opt);
  });
  
  models.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    modelSelect.appendChild(opt);
  });
}

function getHistoryFilters() {
  return {
    endpoint: document.getElementById("history-filter-endpoint").value,
    model: document.getElementById("history-filter-model").value,
    success: document.getElementById("history-filter-success").value,
    starred: document.getElementById("history-filter-starred").value,
    search: document.getElementById("history-filter-search").value.trim()
  };
}

function renderHistoryList(entries) {
  const container = document.getElementById("history-list");
  if (!container) return;
  
  if (!entries || entries.length === 0) {
    container.innerHTML = '<div class="history-empty-state"><p>No history entries found.</p></div>';
    return;
  }
  
  container.innerHTML = "";
  
  entries.forEach(entry => {
    const div = document.createElement("div");
    div.className = "history-entry";
    if (entry.starred) div.classList.add("starred");
    if (!entry.success) div.classList.add("error");
    if (entry.id === selectedHistoryEntryId) div.classList.add("selected");
    div.dataset.id = entry.id;
    
    const preview = entry.prompt || 
      (entry.messages && entry.messages.length > 0 ? entry.messages[entry.messages.length - 1].content : "") ||
      "(no content)";
    
    div.innerHTML = `
      <div class="history-entry-icon">${getEndpointIcon(entry.endpoint)}</div>
      <div class="history-entry-content">
        <div class="history-entry-header">
          <span class="history-entry-endpoint">${entry.endpoint}</span>
          <span class="history-entry-time">${formatTimeAgo(entry.timestamp)}</span>
        </div>
        <div class="history-entry-preview">${escapeHtml(preview.substring(0, 100))}</div>
        <div class="history-entry-meta">
          <span>${entry.model || "unknown"}</span>
          <span>${entry.latency_ms ? entry.latency_ms.toFixed(0) + "ms" : ""}</span>
          <span>${entry.total_tokens ? entry.total_tokens + " tokens" : ""}</span>
          ${entry.starred ? "<span>⭐</span>" : ""}
        </div>
      </div>
    `;
    
    div.addEventListener("click", () => selectHistoryEntry(entry.id));
    container.appendChild(div);
  });
}

async function selectHistoryEntry(entryId) {
  selectedHistoryEntryId = entryId;
  
  // Update UI selection
  document.querySelectorAll(".history-entry").forEach(el => {
    el.classList.toggle("selected", Number(el.dataset.id) === entryId);
  });
  
  // Fetch full entry details
  const res = await fetch(`/api/history/${entryId}`);
  if (!res.ok) return;
  const entry = await res.json();
  
  renderHistoryDetail(entry);
}

function renderHistoryDetail(entry) {
  const container = document.getElementById("history-detail");
  if (!container) return;
  
  const promptContent = entry.prompt || 
    (entry.messages ? JSON.stringify(entry.messages, null, 2) : "(no prompt)");
  
  container.innerHTML = `
    <div class="history-detail-section">
      <h4>Request</h4>
      <div class="history-detail-meta">
        <span>Endpoint:</span><strong>${entry.endpoint}</strong>
        <span>Model:</span><strong>${entry.model || "unknown"}</strong>
        <span>Time:</span><strong>${formatTimestamp(entry.timestamp)}</strong>
        <span>Status:</span><strong>${entry.success ? "✅ Success" : "❌ Error"}</strong>
      </div>
    </div>
    
    ${entry.system_prompt ? `
    <div class="history-detail-section">
      <h4>System Prompt</h4>
      <pre>${escapeHtml(entry.system_prompt)}</pre>
    </div>
    ` : ""}
    
    <div class="history-detail-section">
      <h4>Prompt</h4>
      <pre>${escapeHtml(promptContent)}</pre>
    </div>
    
    <div class="history-detail-section">
      <h4>Response</h4>
      <pre>${entry.error ? `Error: ${escapeHtml(entry.error)}` : escapeHtml(entry.response || "(no response)")}</pre>
    </div>
    
    <div class="history-detail-section">
      <h4>Metrics</h4>
      <div class="history-detail-meta">
        <span>Latency:</span><strong>${entry.latency_ms ? entry.latency_ms.toFixed(1) + "ms" : "N/A"}</strong>
        <span>Prompt Tokens:</span><strong>${entry.prompt_tokens || "N/A"}</strong>
        <span>Completion Tokens:</span><strong>${entry.completion_tokens || "N/A"}</strong>
        <span>Total Tokens:</span><strong>${entry.total_tokens || "N/A"}</strong>
      </div>
    </div>
    
    <div class="history-detail-section">
      <h4>Notes</h4>
      <div class="history-notes-form">
        <textarea id="history-entry-notes" placeholder="Add notes...">${entry.notes || ""}</textarea>
        <button type="button" id="save-history-notes-btn">Save Notes</button>
      </div>
    </div>
    
    <div class="history-detail-actions">
      <button type="button" class="primary" id="replay-entry-btn">🔁 Replay</button>
      <button type="button" class="secondary" id="star-entry-btn">${entry.starred ? "⭐ Unstar" : "☆ Star"}</button>
      <button type="button" class="secondary" id="delete-entry-btn">🗑️ Delete</button>
    </div>
  `;
  
  // Add event handlers
  document.getElementById("save-history-notes-btn").addEventListener("click", () => {
    saveHistoryNotes(entry.id);
  });
  
  document.getElementById("replay-entry-btn").addEventListener("click", () => {
    replayHistoryEntry(entry.id);
  });
  
  document.getElementById("star-entry-btn").addEventListener("click", () => {
    toggleHistoryStar(entry.id, !entry.starred);
  });
  
  document.getElementById("delete-entry-btn").addEventListener("click", () => {
    deleteHistoryEntry(entry.id);
  });
}

async function saveHistoryNotes(entryId) {
  const notes = document.getElementById("history-entry-notes").value;
  
  await fetch(`/api/history/${entryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ notes })
  });
}

async function toggleHistoryStar(entryId, starred) {
  await fetch(`/api/history/${entryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ starred })
  });
  
  await refreshHistoryUI();
  selectHistoryEntry(entryId);
}

async function deleteHistoryEntry(entryId) {
  if (!confirm("Delete this history entry?")) return;
  
  await fetch(`/api/history/${entryId}`, { method: "DELETE" });
  
  selectedHistoryEntryId = null;
  document.getElementById("history-detail").innerHTML = 
    '<p class="history-empty-state">Select an entry to view details</p>';
  
  await refreshHistoryUI();
}

async function replayHistoryEntry(entryId) {
  const replayBtn = document.getElementById("replay-entry-btn");
  replayBtn.disabled = true;
  replayBtn.textContent = "Replaying...";
  
  try {
    const res = await fetch("/api/history/replay", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entry_id: entryId })
    });
    
    const result = await res.json();
    
    if (result.error) {
      alert(`Replay failed: ${result.error}`);
    } else {
      // Show comparison
      alert(`Replay successful!\n\nLatency: ${result.latency_ms.toFixed(0)}ms\n\nOriginal response:\n${result.original_response?.substring(0, 200)}...\n\nNew response:\n${result.response?.substring(0, 200)}...`);
      await refreshHistoryUI();
    }
  } catch (err) {
    alert(`Replay error: ${err.message}`);
  } finally {
    replayBtn.disabled = false;
    replayBtn.textContent = "🔁 Replay";
  }
}

async function clearHistoryData() {
  if (!confirm("Clear all history entries? Starred entries will be kept.")) return;
  
  await fetch("/api/history/clear?keep_starred=true", { method: "POST" });
  await refreshHistoryUI();
}

function updateHistoryPagination(entries) {
  const prevBtn = document.getElementById("history-prev-btn");
  const nextBtn = document.getElementById("history-next-btn");
  const pageInfo = document.getElementById("history-page-info");
  
  prevBtn.disabled = historyPage === 0;
  nextBtn.disabled = entries.length < historyPageSize;
  pageInfo.textContent = `Page ${historyPage + 1}`;
}

async function refreshHistoryUI() {
  const stats = await fetchHistoryStats();
  renderHistoryStats(stats);
  
  await populateHistoryFilters();
  
  const filters = getHistoryFilters();
  const entries = await fetchHistory(filters);
  renderHistoryList(entries);
  updateHistoryPagination(entries);
}

function initHistoryUI() {
  const applyBtn = document.getElementById("history-apply-filter-btn");
  const clearFilterBtn = document.getElementById("history-clear-filter-btn");
  const refreshBtn = document.getElementById("history-refresh-btn");
  const clearBtn = document.getElementById("history-clear-btn");
  const prevBtn = document.getElementById("history-prev-btn");
  const nextBtn = document.getElementById("history-next-btn");
  
  if (!applyBtn) return;
  
  applyBtn.addEventListener("click", () => {
    historyPage = 0;
    refreshHistoryUI();
  });
  
  clearFilterBtn.addEventListener("click", () => {
    document.getElementById("history-filter-endpoint").value = "";
    document.getElementById("history-filter-model").value = "";
    document.getElementById("history-filter-success").value = "";
    document.getElementById("history-filter-starred").value = "";
    document.getElementById("history-filter-search").value = "";
    historyPage = 0;
    refreshHistoryUI();
  });
  
  refreshBtn.addEventListener("click", refreshHistoryUI);
  clearBtn.addEventListener("click", clearHistoryData);
  
  prevBtn.addEventListener("click", () => {
    if (historyPage > 0) {
      historyPage--;
      refreshHistoryUI();
    }
  });
  
  nextBtn.addEventListener("click", () => {
    historyPage++;
    refreshHistoryUI();
  });
  
  // Refresh when tab is selected
  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.getAttribute("data-tab") === "history-tab") {
        refreshHistoryUI();
      }
    });
  });
}


// ========== Latency Dashboard ==========

let dashboardRefreshInterval = null;

function initDashboardUI() {
  const hoursSelect = document.getElementById("dashboard-hours");
  const refreshBtn = document.getElementById("dashboard-refresh-btn");
  const clearBtn = document.getElementById("dashboard-clear-btn");
  
  if (!hoursSelect) return;
  
  hoursSelect.addEventListener("change", () => refreshDashboard());
  refreshBtn.addEventListener("click", () => refreshDashboard());
  clearBtn.addEventListener("click", clearAllMetrics);
  
  // Refresh when tab is selected
  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.getAttribute("data-tab") === "dashboard-tab") {
        refreshDashboard();
      }
    });
  });
}

async function refreshDashboard() {
  const hours = parseInt(document.getElementById("dashboard-hours").value, 10) || 24;
  
  try {
    const [summaryRes, modelsRes, endpointsRes, hourlyRes, recentRes] = await Promise.all([
      fetch(`/api/metrics/summary?hours=${hours}`),
      fetch(`/api/metrics/by-model?hours=${hours}`),
      fetch(`/api/metrics/by-endpoint?hours=${hours}`),
      fetch(`/api/metrics/hourly?hours=${hours}`),
      fetch(`/api/metrics/list?limit=50`)
    ]);
    
    const summary = await summaryRes.json();
    const modelsData = await modelsRes.json();
    const endpointsData = await endpointsRes.json();
    const hourlyData = await hourlyRes.json();
    const recentData = await recentRes.json();
    
    renderDashboardSummary(summary);
    renderModelMetrics(modelsData.models || []);
    renderEndpointMetrics(endpointsData.endpoints || []);
    renderHourlyChart(hourlyData.hourly || []);
    renderRecentRequests(recentData.metrics || []);
    
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

function renderDashboardSummary(summary) {
  document.getElementById("stat-total-requests").textContent = formatNumber(summary.total_requests);
  
  const successRate = summary.total_requests > 0 
    ? ((summary.successful_requests / summary.total_requests) * 100).toFixed(1) 
    : 0;
  document.getElementById("stat-success-rate").textContent = `${successRate}%`;
  
  document.getElementById("stat-avg-latency").textContent = formatLatency(summary.avg_latency_ms);
  document.getElementById("stat-p95-latency").textContent = formatLatency(summary.p95_latency_ms);
  document.getElementById("stat-p99-latency").textContent = formatLatency(summary.p99_latency_ms);
  document.getElementById("stat-total-tokens").textContent = formatNumber(summary.total_tokens);
  document.getElementById("stat-tokens-per-sec").textContent = formatNumber(summary.tokens_per_second?.toFixed(1) || 0);
  document.getElementById("stat-requests-per-min").textContent = formatNumber(summary.requests_per_minute?.toFixed(1) || 0);
}

function renderModelMetrics(models) {
  const tbody = document.querySelector("#model-metrics-table tbody");
  if (!tbody) return;
  
  if (models.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="dashboard-empty">No data available</td></tr>`;
    return;
  }
  
  tbody.innerHTML = models.map(model => `
    <tr>
      <td title="${model.model_name}">${truncateText(model.model_name, 30)}</td>
      <td>${formatNumber(model.request_count)}</td>
      <td class="${getLatencyClass(model.avg_latency_ms)}">${formatLatency(model.avg_latency_ms)}</td>
      <td>${formatNumber(model.total_tokens)}</td>
      <td>
        <div class="success-rate-bar">
          <div class="rate-bar">
            <div class="rate-bar-fill" style="width: ${(model.success_rate * 100).toFixed(0)}%"></div>
          </div>
          <span class="rate-value">${(model.success_rate * 100).toFixed(0)}%</span>
        </div>
      </td>
    </tr>
  `).join("");
}

function renderEndpointMetrics(endpoints) {
  const tbody = document.querySelector("#endpoint-metrics-table tbody");
  if (!tbody) return;
  
  if (endpoints.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="dashboard-empty">No data available</td></tr>`;
    return;
  }
  
  tbody.innerHTML = endpoints.map(ep => `
    <tr>
      <td>${ep.endpoint}</td>
      <td>${formatNumber(ep.request_count)}</td>
      <td class="${getLatencyClass(ep.avg_latency_ms)}">${formatLatency(ep.avg_latency_ms)}</td>
      <td>
        <div class="success-rate-bar">
          <div class="rate-bar">
            <div class="rate-bar-fill" style="width: ${(ep.success_rate * 100).toFixed(0)}%"></div>
          </div>
          <span class="rate-value">${(ep.success_rate * 100).toFixed(0)}%</span>
        </div>
      </td>
    </tr>
  `).join("");
}

function renderHourlyChart(hourlyData) {
  const container = document.getElementById("hourly-chart-container");
  if (!container) return;
  
  if (hourlyData.length === 0) {
    container.innerHTML = `
      <div class="dashboard-empty">
        <div class="dashboard-empty-icon">📊</div>
        <p>No hourly data available</p>
      </div>
    `;
    return;
  }
  
  // Simple bar chart (no external library needed)
  const maxRequests = Math.max(...hourlyData.map(h => h.request_count), 1);
  
  const bars = hourlyData.map(h => {
    const height = (h.request_count / maxRequests) * 100;
    const hour = h.hour.split("T")[1] || h.hour.slice(-2);
    return `
      <div class="chart-bar" style="height: ${height}%">
        <div class="chart-bar-tooltip">
          ${hour}:00<br>
          ${h.request_count} requests<br>
          ${formatLatency(h.avg_latency_ms)} avg
        </div>
      </div>
    `;
  }).join("");
  
  // X-axis labels (show first, middle, last hours)
  const firstHour = hourlyData[0]?.hour?.split("T")[1] || "";
  const lastHour = hourlyData[hourlyData.length - 1]?.hour?.split("T")[1] || "";
  
  container.innerHTML = `
    <div class="chart-bars">${bars}</div>
    <div class="chart-x-labels">
      <span>${firstHour}:00</span>
      <span>Time (hourly)</span>
      <span>${lastHour}:00</span>
    </div>
  `;
}

function renderRecentRequests(metrics) {
  const tbody = document.querySelector("#recent-requests-table tbody");
  if (!tbody) return;
  
  if (metrics.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="dashboard-empty">No recent requests</td></tr>`;
    return;
  }
  
  tbody.innerHTML = metrics.map(m => {
    const timeAgo = formatTimeAgo(m.timestamp);
    const statusBadge = m.success 
      ? `<span class="status-badge success">✓ OK</span>`
      : `<span class="status-badge error">✗ Error</span>`;
    
    return `
      <tr>
        <td class="time-ago" title="${m.timestamp}">${timeAgo}</td>
        <td>${m.endpoint}</td>
        <td title="${m.model_name}">${truncateText(m.model_name, 20)}</td>
        <td class="${getLatencyClass(m.latency_ms)}">${formatLatency(m.latency_ms)}</td>
        <td>${formatNumber(m.total_tokens)}</td>
        <td>${statusBadge}</td>
      </tr>
    `;
  }).join("");
}

async function clearAllMetrics() {
  if (!confirm("Clear all metrics data? This cannot be undone.")) return;
  
  try {
    const res = await fetch("/api/metrics", { method: "DELETE" });
    if (res.ok) {
      refreshDashboard();
    }
  } catch (err) {
    console.error("Failed to clear metrics:", err);
  }
}

// Helper functions
function formatNumber(n) {
  if (n === undefined || n === null) return "0";
  const num = parseFloat(n);
  if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
  if (num >= 1000) return (num / 1000).toFixed(1) + "K";
  return num.toLocaleString();
}

function formatLatency(ms) {
  if (ms === undefined || ms === null) return "0ms";
  if (ms >= 1000) return (ms / 1000).toFixed(2) + "s";
  return Math.round(ms) + "ms";
}

function getLatencyClass(ms) {
  if (ms < 500) return "latency-fast";
  if (ms < 2000) return "latency-medium";
  return "latency-slow";
}

function truncateText(text, maxLen) {
  if (!text) return "";
  return text.length > maxLen ? text.slice(0, maxLen) + "…" : text;
}

function formatTimeAgo(isoString) {
  if (!isoString) return "–";
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHr = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHr / 24);
  
  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${diffDay}d ago`;
}
