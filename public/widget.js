(function (window, document) {
  if (window.SupportGPT) return;

  const HOST = "http://localhost:3000"; // In production, this would be the actual host

  const SupportGPT = {
    config: {},
    isOpen: false,
    
    init: function (config) {
      this.config = config;
      
      // Inject CSS for the container and launcher
      const style = document.createElement("style");
      style.innerHTML = `
        #supportgpt-container {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 999999;
          font-family: system-ui, -apple-system, sans-serif;
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          pointer-events: none;
        }
        
        #supportgpt-iframe {
          width: 380px;
          height: 600px;
          max-height: calc(100vh - 100px);
          border: none;
          border-radius: 12px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.15);
          display: none;
          pointer-events: auto;
          background: transparent;
          margin-bottom: 16px;
          transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
          opacity: 0;
          transform: translateY(10px);
        }
        
        #supportgpt-iframe.open {
          display: block;
          opacity: 1;
          transform: translateY(0);
        }
        
        #supportgpt-launcher {
          width: 60px;
          height: 60px;
          border-radius: 30px;
          background-color: #000;
          color: white;
          border: none;
          cursor: pointer;
          pointer-events: auto;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.2s;
        }
        
        #supportgpt-launcher:hover {
          transform: scale(1.05);
        }
        
        #supportgpt-launcher svg {
          width: 28px;
          height: 28px;
          fill: currentColor;
        }
        
        @media (max-width: 480px) {
          #supportgpt-iframe {
            width: calc(100vw - 40px);
            height: calc(100vh - 120px);
          }
        }
      `;
      document.head.appendChild(style);

      // Create container
      const container = document.createElement("div");
      container.id = "supportgpt-container";

      // Create Iframe
      const iframe = document.createElement("iframe");
      iframe.id = "supportgpt-iframe";
      const queryParams = new URLSearchParams({
        workspaceId: config.workspaceId,
        agentId: config.agentId || ""
      });
      iframe.src = `${HOST}/widget?${queryParams.toString()}`;
      container.appendChild(iframe);

      // Create Launcher button
      const launcher = document.createElement("button");
      launcher.id = "supportgpt-launcher";
      launcher.innerHTML = `
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
        </svg>
      `;
      launcher.onclick = () => this.toggle();
      container.appendChild(launcher);

      document.body.appendChild(container);

      // Listen for messages from iframe
      window.addEventListener("message", (event) => {
        if (event.origin !== HOST) return;
        
        try {
          const data = JSON.parse(event.data);
          if (data.type === "supportgpt:close") {
            this.close();
          } else if (data.type === "supportgpt:config") {
            // Update launcher color based on widget config
            if (data.config && data.config.primary_color) {
              launcher.style.backgroundColor = data.config.primary_color;
            }
          }
        } catch(e) {}
      });
    },
    
    toggle: function() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    },

    open: function() {
      this.isOpen = true;
      const iframe = document.getElementById("supportgpt-iframe");
      const launcher = document.getElementById("supportgpt-launcher");
      if (iframe) iframe.classList.add("open");
      if (launcher) {
        launcher.innerHTML = `
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        `;
      }
      
      // Notify iframe
      iframe.contentWindow.postMessage(JSON.stringify({ type: "supportgpt:opened" }), HOST);
    },

    close: function() {
      this.isOpen = false;
      const iframe = document.getElementById("supportgpt-iframe");
      const launcher = document.getElementById("supportgpt-launcher");
      if (iframe) iframe.classList.remove("open");
      if (launcher) {
        launcher.innerHTML = `
          <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
          </svg>
        `;
      }
    },
    
    identify: function(userPayload) {
       const iframe = document.getElementById("supportgpt-iframe");
       if (iframe) {
           iframe.contentWindow.postMessage(JSON.stringify({ 
               type: "supportgpt:identify", 
               payload: userPayload 
           }), HOST);
       }
    }
  };

  window.SupportGPT = SupportGPT;
})(window, document);
