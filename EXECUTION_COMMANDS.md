# 🚀 SIAC Assistant - Local Execution & Debugging Commands

## 📋 Complete Command Reference

### 1. Server Execution (Python/FastMCP)

**Start the MCP server:**
```bash
cd server/
./start.sh
```

**Manual command (alternative):**
```bash
cd server/
source venv/bin/activate
uvicorn main:app --port 8888 --reload --host 0.0.0.0
```

**Expected output:**
```
🚀 Starting SIAC Assistant MCP Server...
📡 Server will be available at: http://localhost:8888
🔧 MCP endpoint: http://localhost:8888/mcp
```

### 2. Frontend Build (React/TypeScript)

**Build the components:**
```bash
cd web/
./build.sh
```

**Manual commands (alternative):**
```bash
cd web/
npm run clean
npm run build
```

**Expected output:**
```
🎨 Building SIAC Assistant Frontend Components...
✅ Build completed successfully!
📁 Output: dist/template-validation-card.js
📊 Bundle size: 13,498 bytes
```

### 3. HTTPS Tunneling (ngrok)

**Install ngrok:**
```bash
# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

**Start tunnel:**
```bash
ngrok http 8888
```

**Expected output:**
```
Forwarding    https://abc123.ngrok.app -> http://localhost:8888
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.app`) for ChatGPT connection.

### 4. MCP Inspector for Debugging

**Launch MCP Inspector:**
```bash
npx @modelcontextprotocol/inspector@latest
```

**Connect to local server:**
- **URL:** `http://localhost:8888/mcp`
- **Click:** "Connect"

**Verify in Inspector:**
- ✅ All 6 tools listed
- ✅ Tool schemas correct
- ✅ Responses include `structuredContent`
- ✅ `_meta["openai/outputTemplate"]` present

### 5. ChatGPT Developer Mode Connection

**Step 1: Enable Developer Mode**
1. Open ChatGPT (chat.openai.com)
2. Settings → Apps & Connectors → Advanced settings
3. Enable "Developer mode"

**Step 2: Create Connector**
1. Settings → Connectors → Create
2. **Name:** `SIAC Assistant`
3. **Connector URL:** `https://your-ngrok-url.ngrok.app/mcp`
4. **Authentication:** OAuth 2.1

**Step 3: Test Connection**
1. Click "Test Connection"
2. Verify green checkmark
3. Check tools are listed

**Step 4: Use in ChatGPT**
1. Start new conversation
2. Type: "Validate this WhatsApp template: Welcome to our service!"
3. TemplateValidationCard widget should appear
4. Test "Registrar Plantilla" and "Corregir Prompt" buttons

## 🔧 Testing & Verification

### Test MCP Server
```bash
python test_mcp_server.py
```

### Test Frontend Component
```bash
cd web/
open test.html
```

### Verify Integration
1. **Server running:** `curl http://localhost:8888/health`
2. **MCP endpoint:** `curl http://localhost:8888/mcp`
3. **ngrok active:** Visit https://your-url.ngrok.app/mcp
4. **ChatGPT connected:** Test tool calls in ChatGPT

## 🚨 Troubleshooting

### Server Issues
```bash
# Check dependencies
cd server/
source venv/bin/activate
pip list | grep -E "(fastapi|uvicorn|mcp)"

# Check server logs
# (Look at console output from uvicorn)
```

### Frontend Issues
```bash
# Check build
cd web/
npm list
npm run build

# Test locally
open test.html
```

### Connection Issues
```bash
# Test MCP endpoint
curl -X POST http://localhost:8888/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Check ngrok
ngrok status
```

## 📊 Expected Results

### Server Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "siac.validate_template",
        "description": "Use this when you need to validate...",
        "inputSchema": {...},
        "readOnlyHint": true,
        "meta": {
          "openai/outputTemplate": "ui://widget/TemplateValidationCard.html"
        }
      }
    ]
  }
}
```

### Tool Response
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Template validation completed...\n\nStructured Data: {...}\n\nMeta Data: {...}"
      }
    ]
  }
}
```

## 🎯 Success Criteria

- [ ] Server starts on port 8888
- [ ] MCP endpoint responds correctly
- [ ] All 6 tools available
- [ ] Frontend builds successfully
- [ ] ngrok tunnel active
- [ ] MCP Inspector connects
- [ ] ChatGPT connector works
- [ ] Widget renders in ChatGPT
- [ ] Tool calls function properly

---

## 🚀 Quick Start Sequence

**Run these commands in order:**

1. **Start server:** `cd server && ./start.sh`
2. **Build frontend:** `cd web && ./build.sh`
3. **Start tunnel:** `ngrok http 8888`
4. **Launch inspector:** `npx @modelcontextprotocol/inspector@latest`
5. **Connect inspector:** `http://localhost:8888/mcp`
6. **Create ChatGPT connector:** Use ngrok HTTPS URL
7. **Test in ChatGPT:** "Validate this WhatsApp template..."

**Your SIAC Assistant is now ready for end-to-end testing! 🎉**



