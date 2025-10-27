# SIAC Assistant - Local Execution & Debugging Guide

This guide provides step-by-step instructions for running the SIAC Assistant locally, debugging with MCP Inspector, and connecting to ChatGPT in developer mode.

## 🚀 Quick Start Commands

### 1. Server Execution (Python/FastMCP)

**Option A: Using the startup script (Recommended)**
```bash
cd server/
./start.sh
```

**Option B: Manual command**
```bash
cd server/
source venv/bin/activate
uvicorn main:app --port 8888 --reload --host 0.0.0.0
```

**Expected Output:**
```
🚀 Starting SIAC Assistant MCP Server...
========================================
📦 Activating virtual environment...
🌐 Starting FastMCP server on port 8888...
📡 Server will be available at: http://localhost:8888
🔧 MCP endpoint: http://localhost:8888/mcp
```

### 2. Frontend Build (React/TypeScript)

**Option A: Using the build script (Recommended)**
```bash
cd web/
./build.sh
```

**Option B: Manual commands**
```bash
cd web/
npm run clean
npm run build
```

**Expected Output:**
```
🎨 Building SIAC Assistant Frontend Components...
================================================
🧹 Cleaning previous builds...
🔨 Building components...
✅ Build completed successfully!
📁 Output: dist/template-validation-card.js
📊 Bundle size: 13,498 bytes
```

### 3. HTTPS Tunneling (ngrok)

**Install ngrok (if not already installed):**
```bash
# macOS with Homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

**Start ngrok tunnel:**
```bash
ngrok http 8888
```

**Expected Output:**
```
Session Status                online
Account                       your-account (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.app -> http://localhost:8888
```

**Important:** Copy the HTTPS URL (e.g., `https://abc123.ngrok.app`) - you'll need this for ChatGPT connection.

## 🔍 Local Debugging with MCP Inspector

### Install and Launch MCP Inspector

```bash
npx @modelcontextprotocol/inspector@latest
```

### Connect to Local Server

1. **Open MCP Inspector** (usually opens in browser automatically)
2. **Connection URL:** `http://localhost:8888/mcp`
3. **Click "Connect"**

### Verify Server Response

The Inspector will show:
- ✅ **Available Tools:** All 6 tools should be listed
- ✅ **Tool Schemas:** Input/output schemas for each tool
- ✅ **Structured Content:** Verify `structuredContent` in responses
- ✅ **Meta Fields:** Check `_meta["openai/outputTemplate"]` is present

### Test Tool Calls

**Test Read-Only Tools:**
```json
{
  "name": "siac.validate_template",
  "arguments": {
    "template_name": "Test Template",
    "body_text": "This is a test template with {{1}} variable.",
    "category": "Marketing",
    "language_code": "es_ES"
  }
}
```

**Test Write Tools:**
```json
{
  "name": "siac.register_template",
  "arguments": {
    "template_id": "test-123",
    "meta_template_id": "meta-456",
    "client_id": "client-789"
  }
}
```

### Verify Widget Integration

1. **Check Response Structure:** Ensure responses contain both `structuredContent` and `content`
2. **Verify Meta Data:** Confirm `_meta["openai/outputTemplate"]` points to correct widget
3. **Test Widget Rendering:** Use the iframe preview in Inspector

## 🤖 ChatGPT Developer Mode Connection

### Step 1: Enable Developer Mode

1. **Open ChatGPT** (chat.openai.com)
2. **Go to Settings** (gear icon)
3. **Navigate to:** Apps & Connectors → Advanced settings
4. **Enable:** Developer mode

### Step 2: Create Connector

1. **Go to:** Settings → Connectors
2. **Click:** "Create" button
3. **Fill in:**
   - **Name:** `SIAC Assistant`
   - **Description:** `WhatsApp template validation and campaign management`
   - **Connector URL:** `https://your-ngrok-url.ngrok.app/mcp`
   - **Authentication:** OAuth 2.1 (if implemented)

### Step 3: Test Connection

1. **Click:** "Test Connection" button
2. **Verify:** Green checkmark appears
3. **Check:** Available tools are listed

### Step 4: Use in ChatGPT

1. **Start new conversation**
2. **Type:** "Validate this WhatsApp template: Welcome to our service!"
3. **Expected:** TemplateValidationCard widget should appear
4. **Test Actions:** Click "Registrar Plantilla" or "Corregir Prompt" buttons

## 🔧 Development Workflow

### Making Changes

**Backend Changes:**
1. Edit `server/main.py`
2. Server auto-reloads (--reload flag)
3. Test with MCP Inspector

**Frontend Changes:**
1. Edit `web/src/TemplateValidationCard.tsx`
2. Run `npm run build`
3. Refresh ChatGPT connector

**Widget Updates:**
1. Modify component
2. Rebuild frontend
3. **Important:** Use "Refresh" in ChatGPT connector settings

### Debugging Tips

**Server Issues:**
```bash
# Check server logs
tail -f server/logs/app.log

# Test MCP endpoint directly
curl http://localhost:8888/mcp
```

**Frontend Issues:**
```bash
# Test component locally
cd web/
open test.html

# Check build output
ls -la dist/
```

**ChatGPT Connection Issues:**
1. **Verify ngrok is running:** Check https://your-url.ngrok.app/mcp
2. **Check server logs:** Look for connection attempts
3. **Refresh connector:** Use "Refresh" button in ChatGPT settings

## 📋 Verification Checklist

### Server Verification
- [ ] Server starts on port 8888
- [ ] MCP endpoint responds at `/mcp`
- [ ] All 6 tools are available
- [ ] OAuth 2.1 authentication works
- [ ] Tool responses include `structuredContent` and `_meta`

### Frontend Verification
- [ ] Component builds successfully
- [ ] Bundle size is reasonable (~13KB)
- [ ] TemplateValidationCard renders correctly
- [ ] SUCCESS and FAILED scenarios work
- [ ] ChatGPT API integration functions

### Integration Verification
- [ ] ngrok tunnel is active
- [ ] ChatGPT connector connects successfully
- [ ] Widget renders in ChatGPT iframe
- [ ] Tool calls work from ChatGPT
- [ ] Follow-up messages are sent correctly

## 🚨 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check Python environment
cd server/
source venv/bin/activate
python --version
pip list | grep -E "(fastapi|uvicorn|mcp)"
```

**Build fails:**
```bash
# Check Node.js environment
cd web/
node --version
npm --version
npm list
```

**ngrok connection fails:**
```bash
# Check ngrok status
ngrok status
# Restart ngrok
pkill ngrok
ngrok http 8888
```

**ChatGPT can't connect:**
1. Verify HTTPS URL is correct
2. Check server is running
3. Test MCP endpoint manually
4. Refresh connector in ChatGPT

### Log Locations

- **Server logs:** Console output from uvicorn
- **Frontend logs:** Browser console (F12)
- **ngrok logs:** http://127.0.0.1:4040
- **MCP Inspector logs:** Inspector console

## 📞 Support

For issues not covered in this guide:
1. Check server console output
2. Verify all dependencies are installed
3. Test each component individually
4. Use MCP Inspector for detailed debugging

---

**Ready to start? Run these commands in order:**

1. `cd server && ./start.sh`
2. `cd web && ./build.sh`  
3. `ngrok http 8888`
4. `npx @modelcontextprotocol/inspector@latest`
5. Connect Inspector to `http://localhost:8888/mcp`
6. Create ChatGPT connector with ngrok HTTPS URL



