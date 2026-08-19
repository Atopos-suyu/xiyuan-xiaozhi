/* 锡院小智 · 前端逻辑（纯静态，无框架） */
(function () {
  "use strict";

  // 默认后端地址：部署 Zeabur/Render/云服务器后填入，如 "https://xxx.zeabur.app"
  // 留空 = 使用当前页面同源地址（后端托管前端时）
  const DEFAULT_API_BASE = "";

  const WELCOME = [
    "你好！欢迎来到无锡学院，我是你的专属新生助手'锡院小智'🎉",
    "无论你对报到流程、宿舍生活还是选课有任何疑问，都可以随时问我哦！",
    "请问你今天想了解什么？",
  ].join("\n");

  const QUICK_QUESTIONS = [
    "报到流程是什么？",
    "宿舍怎么分配？",
    "怎么选课？",
    "食堂有哪些推荐？",
    "校园卡怎么用？",
    "从火车站怎么到学校？",
  ];

  const chatEl = document.getElementById("chat");
  const inputEl = document.getElementById("input");
  const sendBtn = document.getElementById("sendBtn");
  const quickEl = document.getElementById("quick");
  const toastEl = document.getElementById("toast");

  // ---------- 设置 ----------
  const settingsBtn = document.getElementById("settingsBtn");
  const modal = document.getElementById("settingsModal");
  const apiBaseInput = document.getElementById("apiBase");
  const saveBtn = document.getElementById("saveBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  // 弹窗开关：内联样式 + 移除/添加 hidden 类双保险
  // （.hidden 有 !important，必须移除类才能被内联 display:grid 覆盖）
  function openModal() {
    modal.classList.remove("hidden");
    modal.style.display = "grid";
  }
  function closeModal() {
    modal.classList.add("hidden");
    modal.style.display = "none";
  }

  function getApiBase() {
    try {
      return localStorage.getItem("xiaozhi_api_base") || DEFAULT_API_BASE || "";
    } catch (e) {
      return DEFAULT_API_BASE || ""; // 隐私模式/禁用存储时降级
    }
  }

  function setApiBase(v) {
    try {
      if (v) {
        localStorage.setItem("xiaozhi_api_base", v);
      } else {
        localStorage.removeItem("xiaozhi_api_base");
      }
    } catch (e) {
      /* 存储不可用时仅提示 */
    }
  }

  function apiUrl(path) {
    const base = getApiBase().replace(/\/+$/, "");
    return base ? base + path : path;
  }

  settingsBtn.addEventListener("click", function () {
    apiBaseInput.value = getApiBase();
    openModal();
  });
  saveBtn.addEventListener("click", function () {
    const v = apiBaseInput.value.trim();
    setApiBase(v);
    if (v) {
      showToast("已保存，新地址将在下条消息生效");
    } else {
      showToast("已恢复默认同源地址");
    }
    closeModal();
  });
  cancelBtn.addEventListener("click", closeModal);

  // 点击遮罩（弹窗空白处）关闭
  modal.addEventListener("click", function (e) {
    if (e.target === modal) closeModal();
  });
  // ESC 键关闭
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  // ---------- 渲染 ----------
  function el(tag, cls, html) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (html !== undefined) node.innerHTML = html;
    return node;
  }

  function addMessage(role, text, sources) {
    const wrap = el("div", "msg " + role);
    wrap.appendChild(el("div", "avatar", role === "user" ? "我" : "锡"));
    const bubble = el("div", "bubble", escapeHtml(text));

    if (sources && sources.length) {
      const det = el("details", "sources");
      det.appendChild(el("summary", "", "参考来源（" + sources.length + "）"));
      sources.forEach(function (s) {
        if (!s.url) return;
        const a = el("a", "", escapeHtml(s.title || s.url));
        a.href = s.url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        det.appendChild(a);
      });
      bubble.appendChild(det);
    }
    wrap.appendChild(bubble);
    chatEl.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function scrollToBottom() {
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.remove("hidden");
    setTimeout(function () { toastEl.classList.add("hidden"); }, 2500);
  }

  // ---------- 快捷问题 ----------
  QUICK_QUESTIONS.forEach(function (q) {
    const b = el("button", "", q);
    b.addEventListener("click", function () {
      inputEl.value = q;
      send();
    });
    quickEl.appendChild(b);
  });

  // ---------- 发送 ----------
  async function send() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = "";
    addMessage("user", text);

    const typing = addMessage("ai", "正在思考…");
    typing.classList.add("typing");
    sendBtn.disabled = true;

    try {
      const resp = await fetch(apiUrl("/api/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: "web-" + getSessionId() }),
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      const data = await resp.json();
      typing.classList.remove("typing");
      typing.querySelector(".bubble").textContent = data.reply || "（无回复）";
      if (data.sources && data.sources.length) {
        const det = el("details", "sources");
        det.appendChild(el("summary", "", "参考来源（" + data.sources.length + "）"));
        data.sources.forEach(function (s) {
          if (!s.url) return;
          const a = el("a", "", escapeHtml(s.title || s.url));
          a.href = s.url;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          det.appendChild(a);
        });
        typing.querySelector(".bubble").appendChild(det);
      }
    } catch (err) {
      typing.classList.remove("typing");
      typing.querySelector(".bubble").textContent =
        "连接后端失败，请检查设置中的 API 地址，或稍后再试。" +
        (getApiBase() ? "" : "（当前使用同源地址，未配置后端时请点击右上角⚙️设置）");
    } finally {
      sendBtn.disabled = false;
      scrollToBottom();
    }
  }

  function getSessionId() {
    let sid = localStorage.getItem("xiaozhi_session_id");
    if (!sid) {
      sid = "s" + Date.now() + Math.random().toString(36).slice(2, 8);
      localStorage.setItem("xiaozhi_session_id", sid);
    }
    return sid;
  }

  sendBtn.addEventListener("click", send);
  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  // 自动增高输入框
  inputEl.addEventListener("input", function () {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + "px";
  });

  // ---------- 初始化 ----------
  addMessage("ai", WELCOME);
  inputEl.focus();
})();
