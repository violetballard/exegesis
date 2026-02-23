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
    return {
      type: "GenericCard",
      title: String(card.title || "Untitled"),
      subtitle: typeof card.subtitle === "string" ? card.subtitle : "",
      blocks: blocks,
      actions: Array.isArray(card.actions) ? card.actions : [],
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
  }

  function getCSRFToken() {
    var fromMeta = document.querySelector('meta[name="csrf-token"]');
    return fromMeta && fromMeta.content ? fromMeta.content : "";
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
      if (!target.dataset.actionId) {
        return;
      }
      var payload = parseJSON(target.dataset.actionPayload || "{}") || {};
      var endpoint = root.dataset.actionsUrl || "/api/actions/execute";
      fetch(endpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-csrf-token": getCSRFToken(),
        },
        credentials: "same-origin",
        body: JSON.stringify({ id: target.dataset.actionId, payload: payload }),
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
      return;
    }
    var source = new EventSource(streamUrl, { withCredentials: true });

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
      appendEvent(eventsNode, "done", parseJSON(event.data) || {});
      source.close();
    });

    source.onerror = function () {
      appendEvent(eventsNode, "error", { reason: "stream disconnected" });
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
      bindTerminalSend(terminalRoot);
      bindCardActions(terminalRoot);
      startTerminalStream(terminalRoot);
    }
    var probePanel = document.getElementById("provider-probe-panel");
    if (probePanel) {
      bindProbePanel(probePanel);
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
