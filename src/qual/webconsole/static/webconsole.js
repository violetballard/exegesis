(function () {
  "use strict";

  var PRIMITIVE_BLOCK_TYPES = new Set([
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
  ]);
  var ALLOWED_ACTION_IDS = new Set([
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "run_agent",
    "refresh_license",
    "export_document",
    "copy_to_clipboard",
  ]);
  var ACTION_SCHEMAS = {
    apply_patch: { patch_id: "string" },
    reject_patch: { patch_id: "string" },
    open_section: { section_id: "string" },
    open_corpus_item: { item_id: "string" },
    pin_to_context_set: { item_id: "string" },
    create_context_set: { name: "string" },
    run_agent: { operation: "string" },
    refresh_license: {},
    export_document: { format: "string" },
    copy_to_clipboard: { text: "string" },
  };
  var MAX_EVENT_ROWS = 200;
  var MAX_RECONNECT_ATTEMPTS = 5;
  var RECONNECT_BASE_MS = 1000;
  var RECONNECT_MAX_MS = 10000;

  function parseJSON(input) {
    try {
      return JSON.parse(input);
    } catch (_err) {
      return null;
    }
  }

  function createElement(tag, className, text) {
    var el = document.createElement(tag);
    if (className) {
      el.className = className;
    }
    if (typeof text === "string") {
      el.textContent = text;
    }
    return el;
  }

  function payloadMatchesSchema(actionId, payload) {
    var schema = ACTION_SCHEMAS[actionId];
    if (!schema) {
      return false;
    }
    var keys = Object.keys(schema);
    for (var i = 0; i < keys.length; i += 1) {
      var key = keys[i];
      if (!(key in payload)) {
        return false;
      }
      if (typeof payload[key] !== schema[key]) {
        return false;
      }
    }
    return true;
  }

  function renderBlock(block) {
    var type = typeof block.type === "string" ? block.type : "";
    if (!PRIMITIVE_BLOCK_TYPES.has(type)) {
      return createElement("div", "block", "Unsupported block");
    }
    if (type === "MarkdownBlock") {
      return createElement("pre", "block code-json", String(block.markdown || ""));
    }
    if (type === "AlertBlock") {
      return createElement("div", "block warning", String(block.message || ""));
    }
    if (type === "CodeBlock") {
      return createElement("pre", "block code-json", String(block.code || ""));
    }
    if (type === "ProgressBlock") {
      var progressText = String(block.title || "progress") + ": " + String(block.status_text || "");
      return createElement("div", "block", progressText);
    }
    if (type === "KeyValueBlock") {
      var kv = createElement("div", "block");
      var items = Array.isArray(block.items) ? block.items : [];
      items.forEach(function (item) {
        if (!item || typeof item !== "object") {
          return;
        }
        kv.appendChild(createElement("div", "", String(item.key || "") + ": " + String(item.value || "")));
      });
      return kv;
    }
    if (type === "ListBlock") {
      var ul = createElement("ul", "block");
      var list = Array.isArray(block.items) ? block.items : [];
      list.forEach(function (item) {
        ul.appendChild(createElement("li", "", typeof item === "string" ? item : String((item && item.label) || "")));
      });
      return ul;
    }
    if (type === "TableBlock") {
      var table = createElement("table", "block");
      var headers = Array.isArray(block.columns) ? block.columns : [];
      var rows = Array.isArray(block.rows) ? block.rows : [];
      if (headers.length) {
        var thead = createElement("thead");
        var trh = createElement("tr");
        headers.forEach(function (header) {
          trh.appendChild(createElement("th", "", String(header)));
        });
        thead.appendChild(trh);
        table.appendChild(thead);
      }
      var tbody = createElement("tbody");
      rows.forEach(function (row) {
        var tr = createElement("tr");
        if (Array.isArray(row)) {
          row.forEach(function (cell) {
            tr.appendChild(createElement("td", "", String(cell)));
          });
        }
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      return table;
    }
    return createElement("div", "block", "Unsupported block");
  }

  function buildUnknownCard(rawCard) {
    var type = rawCard && typeof rawCard.type === "string" ? rawCard.type : "<missing>";
    var nestedBlocks = [];
    if (Array.isArray(rawCard && rawCard.blocks)) {
      rawCard.blocks.forEach(function (block) {
        if (block && typeof block === "object" && PRIMITIVE_BLOCK_TYPES.has(String(block.type || ""))) {
          nestedBlocks.push(block);
        }
      });
    }
    nestedBlocks.push({
      type: "CodeBlock",
      code: JSON.stringify(rawCard, null, 2),
      language: "json",
      collapsed: true,
    });
    return {
      type: "UnknownCard",
      title: "Unsupported card type: " + type,
      blocks: nestedBlocks,
      actions: [
        {
          id: "copy_to_clipboard",
          label: "Copy JSON",
          payload: { text: JSON.stringify(rawCard, null, 2) },
        },
      ],
    };
  }

  function materializeCard(card) {
    if (!card || typeof card !== "object") {
      return buildUnknownCard({ type: "<invalid>", payload: card });
    }
    if (card.type !== "GenericCard") {
      return buildUnknownCard(card);
    }
    var blocks = Array.isArray(card.blocks)
      ? card.blocks.filter(function (block) {
          return block && typeof block === "object" && PRIMITIVE_BLOCK_TYPES.has(String(block.type || ""));
        })
      : [];
    var actions = Array.isArray(card.actions)
      ? card.actions.filter(function (action) {
          var actionId = String((action && action.id) || "");
          var payload = action && action.payload;
          return (
            action &&
            typeof action === "object" &&
            ALLOWED_ACTION_IDS.has(actionId) &&
            typeof action.label === "string" &&
            action.label.trim() &&
            payload &&
            typeof payload === "object" &&
            !Array.isArray(payload) &&
            payloadMatchesSchema(actionId, payload)
          );
        })
      : [];
    return {
      type: "GenericCard",
      title: String(card.title || "Untitled"),
      subtitle: typeof card.subtitle === "string" ? card.subtitle : "",
      blocks: blocks,
      actions: actions,
    };
  }

  function renderCard(card) {
    var materialized = materializeCard(card);
    var wrapper = createElement("article", "card");
    wrapper.appendChild(createElement("h4", "", materialized.title));
    if (materialized.subtitle) {
      wrapper.appendChild(createElement("p", "subtitle", materialized.subtitle));
    }
    materialized.blocks.forEach(function (block) {
      wrapper.appendChild(renderBlock(block));
    });
    var actions = Array.isArray(materialized.actions) ? materialized.actions : [];
    if (actions.length > 0) {
      var row = createElement("div", "probe-actions-row");
      actions.forEach(function (action) {
        if (!action || typeof action !== "object") {
          return;
        }
        var button = createElement("button", "", String(action.label || "Action"));
        button.type = "button";
        button.dataset.actionId = String(action.id || "");
        button.dataset.actionPayload = JSON.stringify(action.payload || {});
        row.appendChild(button);
      });
      wrapper.appendChild(row);
    }
    return wrapper;
  }

  function appendEvent(eventsNode, eventType, payload) {
    if (!eventsNode) {
      return;
    }
    eventsNode.appendChild(createElement("li", "", eventType + ": " + JSON.stringify(payload)));
    while (eventsNode.children.length > MAX_EVENT_ROWS) {
      eventsNode.removeChild(eventsNode.firstChild);
    }
  }

  function getCSRFToken() {
    var fromMeta = document.querySelector('meta[name="csrf-token"]');
    return fromMeta && fromMeta.content ? fromMeta.content : "";
  }

  function setStreamStatus(root, status, label) {
    var statusNode = root.querySelector("#terminal-stream-status");
    if (!statusNode) {
      return;
    }
    statusNode.className = "status-pill status-" + status;
    statusNode.textContent = label;
  }

  function setRetryInfo(root, label) {
    var infoNode = root.querySelector("#terminal-retry-info");
    if (!infoNode) {
      return;
    }
    infoNode.textContent = label || "";
  }

  function setAutoRetryButtonLabel(root) {
    var button = root.querySelector("[data-stream-autoretry-toggle]");
    if (!button) {
      return;
    }
    var enabled = root._autoRetryEnabled !== false;
    button.textContent = enabled ? "Auto-retry: on" : "Auto-retry: off";
    button.setAttribute("aria-pressed", enabled ? "true" : "false");
  }

  function isEditableTarget(target) {
    if (!target || !(target instanceof Element)) {
      return false;
    }
    var tag = target.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable;
  }

  function setControlState(root, state) {
    var reconnectButton = root.querySelector("[data-stream-reconnect]");
    if (reconnectButton) {
      var connecting = state === "connecting";
      reconnectButton.disabled = connecting;
      reconnectButton.textContent = connecting ? "Connecting..." : "Reconnect";
      reconnectButton.setAttribute("aria-disabled", connecting ? "true" : "false");
    }
  }

  function clearReconnectState(root) {
    if (root._reconnectTimer) {
      clearTimeout(root._reconnectTimer);
      root._reconnectTimer = null;
    }
    if (root._reconnectTickTimer) {
      clearInterval(root._reconnectTickTimer);
      root._reconnectTickTimer = null;
    }
    setRetryInfo(root, "");
  }

  function scheduleReconnect(root) {
    if (root._autoRetryEnabled === false) {
      setRetryInfo(root, "Auto-reconnect off");
      return;
    }
    var attempts = Number(root._retryAttempt || 0) + 1;
    root._retryAttempt = attempts;
    if (attempts > MAX_RECONNECT_ATTEMPTS) {
      setRetryInfo(root, "Auto-reconnect paused");
      return;
    }
    var delayMs = Math.min(RECONNECT_MAX_MS, RECONNECT_BASE_MS * Math.pow(2, attempts - 1));
    var remainingSeconds = Math.ceil(delayMs / 1000);
    setRetryInfo(root, "Retrying in " + String(remainingSeconds) + "s");
    root._reconnectTickTimer = setInterval(function () {
      remainingSeconds -= 1;
      if (remainingSeconds <= 0) {
        clearReconnectState(root);
        return;
      }
      setRetryInfo(root, "Retrying in " + String(remainingSeconds) + "s");
    }, 1000);
    root._reconnectTimer = setTimeout(function () {
      clearReconnectState(root);
      startTerminalStream(root);
    }, delayMs);
  }

  function bindTerminalSend(root) {
    var form = root.querySelector("#terminal-send-form");
    if (!form) {
      return;
    }
    var input = root.querySelector("#terminal-input");
    var sendUrl = root.dataset.sendUrl || "/api/terminal/send";
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var message = input ? input.value : "";
      if (!message) {
        return;
      }
      fetch(sendUrl, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-csrf-token": getCSRFToken(),
        },
        credentials: "same-origin",
        body: JSON.stringify({ message: message, session_id: root.dataset.sessionId || "" }),
      }).finally(function () {
        if (input) {
          input.value = "";
        }
      });
    });
  }

  function bindCardActions(root) {
    root.addEventListener("click", function (event) {
      var target = event.target;
      if (!(target instanceof HTMLButtonElement)) {
        return;
      }
      var actionId = String(target.dataset.actionId || "");
      if (!actionId || !ALLOWED_ACTION_IDS.has(actionId)) {
        return;
      }
      var payload = parseJSON(target.dataset.actionPayload || "{}") || {};
      if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
        return;
      }
      if (!payloadMatchesSchema(actionId, payload)) {
        return;
      }

      if (actionId === "copy_to_clipboard") {
        var text = typeof payload.text === "string" ? payload.text : "";
        if (!text) {
          return;
        }
        if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
          navigator.clipboard.writeText(text);
        }
        return;
      }

      var endpoint = root.dataset.actionsUrl || "/api/actions/execute";
      fetch(endpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-csrf-token": getCSRFToken(),
        },
        credentials: "same-origin",
        body: JSON.stringify({ id: actionId, payload: payload }),
      });
    });
  }

  function startTerminalStream(root) {
    var transcriptNode = root.querySelector("#terminal-transcript");
    var cardsNode = root.querySelector("#terminal-cards");
    var eventsNode = root.querySelector("#terminal-events");
    var streamUrl = root.dataset.streamUrl;
    if (!streamUrl) {
      appendEvent(eventsNode, "error", { reason: "missing stream url" });
      setStreamStatus(root, "disconnected", "Missing stream URL");
      setControlState(root, "disconnected");
      return;
    }
    clearReconnectState(root);
    if (root._terminalSource) {
      root._terminalSource.close();
      root._terminalSource = null;
    }
    setStreamStatus(root, "connecting", "Connecting...");
    setControlState(root, "connecting");
    var source = new EventSource(streamUrl, { withCredentials: true });
    var streamClosed = false;
    root._terminalSource = source;

    source.onopen = function () {
      if (streamClosed) {
        return;
      }
      root._retryAttempt = 0;
      setStreamStatus(root, "connected", "Connected");
      setControlState(root, "connected");
    };

    source.addEventListener("message.delta", function (event) {
      var payload = parseJSON(event.data) || {};
      var delta = String(payload.delta || payload.text || "");
      if (transcriptNode) {
        transcriptNode.textContent += delta;
      }
    });

    source.addEventListener("card", function (event) {
      var payload = parseJSON(event.data) || {};
      var cardPayload = payload.card && typeof payload.card === "object" ? payload.card : payload;
      if (cardsNode) {
        cardsNode.appendChild(renderCard(cardPayload));
      }
    });

    ["tool.call", "tool.result", "progress"].forEach(function (eventType) {
      source.addEventListener(eventType, function (event) {
        appendEvent(eventsNode, eventType, parseJSON(event.data) || {});
      });
    });

    source.addEventListener("done", function (event) {
      if (streamClosed) {
        return;
      }
      appendEvent(eventsNode, "done", parseJSON(event.data) || {});
      streamClosed = true;
      setStreamStatus(root, "completed", "Completed");
      setControlState(root, "completed");
      clearReconnectState(root);
      source.close();
      root._terminalSource = null;
    });

    source.onerror = function () {
      if (streamClosed) {
        return;
      }
      appendEvent(eventsNode, "error", { reason: "stream disconnected" });
      streamClosed = true;
      setStreamStatus(root, "disconnected", "Disconnected");
      setControlState(root, "disconnected");
      source.close();
      root._terminalSource = null;
      scheduleReconnect(root);
    };
  }

  function renderProbePanel(panel, report) {
    var base = panel.querySelector(".kv-grid");
    if (base) {
      while (base.firstChild) {
        base.removeChild(base.firstChild);
      }
      [
        ["Base URL", (report.provider && report.provider.base_url) || "<unknown>"],
        ["Timestamp", report.timestamp || "<unknown>"],
        ["Streaming", String(Boolean(report.streaming))],
        ["Tool calling", String(report.tool_calling || "unknown")],
        ["Vision", String(Boolean(report.vision))],
      ].forEach(function (entry) {
        var item = createElement("div");
        item.appendChild(createElement("strong", "", entry[0]));
        item.appendChild(createElement("span", "", String(entry[1])));
        base.appendChild(item);
      });
    }

    var roles = panel.querySelector("#probe-role-list");
    if (roles) {
      while (roles.firstChild) {
        roles.removeChild(roles.firstChild);
      }
      var roleMap = report.roles_available && typeof report.roles_available === "object" ? report.roles_available : {};
      Object.keys(roleMap)
        .sort()
        .forEach(function (role) {
          roles.appendChild(createElement("li", "", role + ": " + (roleMap[role] ? "available" : "missing")));
        });
      if (!roles.children.length) {
        roles.appendChild(createElement("li", "", "No role availability data."));
      }
    }

    var actions = panel.querySelector("#probe-actions-list");
    if (actions) {
      while (actions.firstChild) {
        actions.removeChild(actions.firstChild);
      }
      var actionList = Array.isArray(report.recommended_actions) ? report.recommended_actions : [];
      actionList.forEach(function (line) {
        actions.appendChild(createElement("li", "", String(line)));
      });
      if (!actions.children.length) {
        actions.appendChild(createElement("li", "", "No recommended actions."));
      }
    }

    var raw = panel.querySelector("#probe-report-raw");
    if (raw) {
      raw.textContent = JSON.stringify(report, null, 2);
    }
  }

  function fetchProbeReport(panel) {
    var reportUrl = panel.dataset.probeReportUrl || "/api/provider/probe_report";
    return fetch(reportUrl, { method: "GET", credentials: "same-origin" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error("probe report fetch failed");
        }
        return response.json();
      })
      .then(function (report) {
        renderProbePanel(panel, report || {});
      });
  }

  function rerunProbe(panel) {
    var rerunUrl = panel.dataset.probeRerunUrl || "/api/provider/probe";
    return fetch(rerunUrl, {
      method: "POST",
      headers: { "x-csrf-token": getCSRFToken() },
      credentials: "same-origin",
    }).then(function () {
      return fetchProbeReport(panel);
    });
  }

  function bindProbePanel(panel) {
    panel.addEventListener("click", function (event) {
      var target = event.target;
      if (!(target instanceof HTMLButtonElement)) {
        return;
      }
      if (target.hasAttribute("data-probe-refresh")) {
        fetchProbeReport(panel);
      }
      if (target.hasAttribute("data-probe-rerun")) {
        rerunProbe(panel);
      }
    });
  }

  function init() {
    var terminalRoot = document.getElementById("terminal-root");
    if (terminalRoot) {
      terminalRoot._autoRetryEnabled = true;
      setAutoRetryButtonLabel(terminalRoot);
      setControlState(terminalRoot, "connecting");
      bindTerminalSend(terminalRoot);
      bindCardActions(terminalRoot);
      startTerminalStream(terminalRoot);
      var reconnectButton = terminalRoot.querySelector("[data-stream-reconnect]");
      if (reconnectButton) {
        reconnectButton.addEventListener("click", function () {
          terminalRoot._retryAttempt = 0;
          clearReconnectState(terminalRoot);
          startTerminalStream(terminalRoot);
        });
      }
      var autoRetryButton = terminalRoot.querySelector("[data-stream-autoretry-toggle]");
      if (autoRetryButton) {
        autoRetryButton.addEventListener("click", function () {
          terminalRoot._autoRetryEnabled = terminalRoot._autoRetryEnabled === false;
          setAutoRetryButtonLabel(terminalRoot);
          if (terminalRoot._autoRetryEnabled === false) {
            clearReconnectState(terminalRoot);
            setRetryInfo(terminalRoot, "Auto-reconnect off");
          } else if (!terminalRoot._terminalSource) {
            setRetryInfo(terminalRoot, "Auto-reconnect enabled");
          }
        });
      }
      document.addEventListener("keydown", function (event) {
        if (!event.altKey || event.shiftKey || event.metaKey || event.ctrlKey) {
          return;
        }
        if (isEditableTarget(event.target)) {
          return;
        }
        var key = String(event.key || "").toLowerCase();
        if (key === "r") {
          event.preventDefault();
          terminalRoot._retryAttempt = 0;
          clearReconnectState(terminalRoot);
          startTerminalStream(terminalRoot);
          return;
        }
        if (key === "a") {
          event.preventDefault();
          terminalRoot._autoRetryEnabled = terminalRoot._autoRetryEnabled === false;
          setAutoRetryButtonLabel(terminalRoot);
          if (terminalRoot._autoRetryEnabled === false) {
            clearReconnectState(terminalRoot);
            setRetryInfo(terminalRoot, "Auto-reconnect off");
          } else if (!terminalRoot._terminalSource) {
            setRetryInfo(terminalRoot, "Auto-reconnect enabled");
          }
        }
      });
    }
    var probePanel = document.getElementById("provider-probe-panel");
    if (probePanel) {
      bindProbePanel(probePanel);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
