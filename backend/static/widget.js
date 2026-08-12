(function() {
    // Zero Dependency Vanilla JS SDK for SupportGPT
    window.SupportGPT = window.SupportGPT || {};

    let sessionToken = localStorage.getItem('supportgpt_session') || null;
    let config = null;
    let container = null;

    SupportGPT.init = async function(options) {
        if (!options.workspaceId || !options.agentId) {
            console.error("SupportGPT: workspaceId and agentId are required.");
            return;
        }

        // Fetch Config
        try {
            const res = await fetch(`http://localhost:8000/api/v1/widget/config/${options.agentId}`);
            config = await res.json();
            
            // Generate Session if none
            if (!sessionToken) {
                const sessionRes = await fetch(`http://localhost:8000/api/v1/widget/session`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        workspace_id: options.workspaceId,
                        agent_id: options.agentId
                    })
                });
                const sessionData = await sessionRes.json();
                sessionToken = sessionData.session_token;
                localStorage.setItem('supportgpt_session', sessionToken);
            }
            
            // Build UI
            buildWidget();
        } catch (e) {
            console.error("SupportGPT Failed to initialize:", e);
        }
    };

    function buildWidget() {
        if (container) return; // Already built

        // Main Container
        container = document.createElement('div');
        container.id = "supportgpt-widget-container";
        
        // Setup inline styles
        const styles = document.createElement('style');
        styles.innerHTML = `
            #supportgpt-widget-container {
                position: fixed;
                ${config.position === 'bottom-left' ? 'left: 20px;' : 'right: 20px;'}
                bottom: 20px;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            #supportgpt-launcher {
                background-color: ${config.primary_color || '#000'};
                color: #fff;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            #supportgpt-chat {
                display: none;
                flex-direction: column;
                position: absolute;
                bottom: 80px;
                ${config.position === 'bottom-left' ? 'left: 0;' : 'right: 0;'}
                width: 350px;
                height: 500px;
                background: ${config.theme === 'dark' ? '#1f2937' : '#fff'};
                color: ${config.theme === 'dark' ? '#f3f4f6' : '#111827'};
                border-radius: ${config.border_radius || '8px'};
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            #supportgpt-chat-header {
                background-color: ${config.primary_color || '#000'};
                color: #fff;
                padding: 15px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
            }
            #supportgpt-chat-body {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .supportgpt-msg {
                padding: 10px;
                border-radius: 8px;
                max-width: 80%;
            }
            .supportgpt-msg-user {
                background: #e5e7eb;
                color: #000;
                align-self: flex-end;
            }
            .supportgpt-msg-ai {
                background: ${config.primary_color || '#000'};
                color: #fff;
                align-self: flex-start;
            }
            #supportgpt-chat-input-container {
                display: flex;
                padding: 10px;
                border-top: 1px solid #e5e7eb;
            }
            #supportgpt-chat-input {
                flex: 1;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                outline: none;
            }
            #supportgpt-chat-send {
                background-color: ${config.primary_color || '#000'};
                color: white;
                border: none;
                border-radius: 4px;
                margin-left: 5px;
                cursor: pointer;
                padding: 0 15px;
            }
        `;
        document.head.appendChild(styles);

        // Launcher
        const launcher = document.createElement('div');
        launcher.id = "supportgpt-launcher";
        launcher.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;
        
        // Chat Window
        const chat = document.createElement('div');
        chat.id = "supportgpt-chat";
        
        chat.innerHTML = `
            <div id="supportgpt-chat-header">
                <span>${config.launcher_text || "Chat"}</span>
                <span id="supportgpt-chat-close" style="cursor: pointer;">&times;</span>
            </div>
            <div id="supportgpt-chat-body">
                <div class="supportgpt-msg supportgpt-msg-ai">${config.welcome_message || "Hello! How can I help?"}</div>
            </div>
            <div id="supportgpt-chat-input-container">
                <input type="text" id="supportgpt-chat-input" placeholder="Type a message..." />
                <button id="supportgpt-chat-send">Send</button>
            </div>
        `;

        container.appendChild(chat);
        container.appendChild(launcher);
        document.body.appendChild(container);

        // Events
        let isOpen = false;
        launcher.addEventListener('click', () => {
            isOpen = !isOpen;
            chat.style.display = isOpen ? 'flex' : 'none';
        });
        
        document.getElementById('supportgpt-chat-close').addEventListener('click', () => {
            isOpen = false;
            chat.style.display = 'none';
        });

        const sendBtn = document.getElementById('supportgpt-chat-send');
        const input = document.getElementById('supportgpt-chat-input');
        const body = document.getElementById('supportgpt-chat-body');

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            // Render User
            body.innerHTML += `<div class="supportgpt-msg supportgpt-msg-user">${text}</div>`;
            input.value = "";
            body.scrollTop = body.scrollHeight;

            // Send to Backend
            try {
                const res = await fetch(`http://localhost:8000/api/v1/widget/message`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_token: sessionToken,
                        content: text
                    })
                });
                const data = await res.json();
                
                // Render AI
                body.innerHTML += `<div class="supportgpt-msg supportgpt-msg-ai">${data.reply || "Sorry, I couldn't understand that."}</div>`;
                body.scrollTop = body.scrollHeight;
            } catch (e) {
                console.error("SupportGPT message failed", e);
            }
        }

        sendBtn.addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

})();
