(function() {
  if (window.SupportGPTWidget) return;

  const scriptTag = document.currentScript;
  let workspaceId = scriptTag ? scriptTag.getAttribute('data-workspace-id') : null;
  let agentId = scriptTag ? scriptTag.getAttribute('data-agent-id') : null;
  const baseUrl = scriptTag ? scriptTag.getAttribute('data-base-url') || "http://localhost:3000" : "http://localhost:3000";

  let widgetContainer = null;
  let iframe = null;
  let launcherBtn = null;
  let isOpen = false;

  window.SupportGPTWidget = {
    init: function(config) {
      if (config.workspaceId) workspaceId = config.workspaceId;
      if (config.agentId) agentId = config.agentId;
      
      if (!workspaceId) {
        console.error("SupportGPT Widget: workspaceId is required.");
        return;
      }

      this._createWidgetElements();
      this._setupEventListeners();
    },

    _createWidgetElements: function() {
      // Container
      widgetContainer = document.createElement("div");
      widgetContainer.id = "supportgpt-widget-container";
      widgetContainer.style.position = "fixed";
      widgetContainer.style.bottom = "20px";
      widgetContainer.style.right = "20px";
      widgetContainer.style.zIndex = "999999";
      widgetContainer.style.fontFamily = "system-ui, -apple-system, sans-serif";
      
      // Launcher Button
      launcherBtn = document.createElement("button");
      launcherBtn.id = "supportgpt-launcher";
      launcherBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>`;
      launcherBtn.style.width = "60px";
      launcherBtn.style.height = "60px";
      launcherBtn.style.borderRadius = "50%";
      launcherBtn.style.backgroundColor = "#000000";
      launcherBtn.style.color = "#ffffff";
      launcherBtn.style.border = "none";
      launcherBtn.style.cursor = "pointer";
      launcherBtn.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
      launcherBtn.style.display = "flex";
      launcherBtn.style.alignItems = "center";
      launcherBtn.style.justifyContent = "center";
      launcherBtn.style.transition = "transform 0.2s ease";
      
      // Iframe container
      const iframeWrapper = document.createElement("div");
      iframeWrapper.id = "supportgpt-iframe-wrapper";
      iframeWrapper.style.position = "absolute";
      iframeWrapper.style.bottom = "80px";
      iframeWrapper.style.right = "0";
      iframeWrapper.style.width = "380px";
      iframeWrapper.style.height = "600px";
      iframeWrapper.style.maxHeight = "calc(100vh - 100px)";
      iframeWrapper.style.backgroundColor = "#ffffff";
      iframeWrapper.style.borderRadius = "16px";
      iframeWrapper.style.boxShadow = "0 8px 32px rgba(0,0,0,0.16)";
      iframeWrapper.style.overflow = "hidden";
      iframeWrapper.style.display = "none";
      iframeWrapper.style.opacity = "0";
      iframeWrapper.style.transform = "translateY(10px)";
      iframeWrapper.style.transition = "opacity 0.2s ease, transform 0.2s ease";

      iframe = document.createElement("iframe");
      const url = new URL(`${baseUrl}/widget`);
      url.searchParams.set("workspaceId", workspaceId);
      if (agentId) url.searchParams.set("agentId", agentId);
      
      iframe.src = url.toString();
      iframe.style.width = "100%";
      iframe.style.height = "100%";
      iframe.style.border = "none";

      iframeWrapper.appendChild(iframe);
      widgetContainer.appendChild(iframeWrapper);
      widgetContainer.appendChild(launcherBtn);
      document.body.appendChild(widgetContainer);

      launcherBtn.addEventListener("click", () => this.toggle());
    },

    _setupEventListeners: function() {
      window.addEventListener("message", (e) => {
        // Ensure origin is safe in production
        try {
          const data = JSON.parse(e.data);
          
          if (data.type === "supportgpt:close") {
            this.close();
          } else if (data.type === "supportgpt:config" && data.config) {
             if (data.config.primary_color && launcherBtn) {
                 launcherBtn.style.backgroundColor = data.config.primary_color;
             }
             if (data.config.launcher_text && launcherBtn) {
                 // You can add text to the launcher if needed
             }
          }
        } catch (err) {}
      });
    },

    toggle: function() {
      if (isOpen) {
        this.close();
      } else {
        this.open();
      }
    },

    open: function() {
      const wrapper = document.getElementById("supportgpt-iframe-wrapper");
      if (wrapper) {
        wrapper.style.display = "block";
        // trigger reflow
        void wrapper.offsetWidth;
        wrapper.style.opacity = "1";
        wrapper.style.transform = "translateY(0)";
        isOpen = true;
        
        launcherBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>`;
      }
    },

    close: function() {
      const wrapper = document.getElementById("supportgpt-iframe-wrapper");
      if (wrapper) {
        wrapper.style.opacity = "0";
        wrapper.style.transform = "translateY(10px)";
        setTimeout(() => {
          if (!isOpen) wrapper.style.display = "none";
        }, 200);
        isOpen = false;
        
        launcherBtn.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>`;
      }
    }
  };

  // Auto-init if attributes are present
  if (workspaceId) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
        window.SupportGPTWidget.init({});
    } else {
        document.addEventListener("DOMContentLoaded", () => {
            window.SupportGPTWidget.init({});
        });
    }
  }

})();
