#!/bin/bash
# SIAC Assistant - Server Startup Script
# This script starts the FastMCP server for local development

echo "🚀 Starting SIAC Assistant MCP Server..."
echo "========================================"

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the server/ directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi, uvicorn, mcp" 2>/dev/null; then
    echo "❌ Error: Required dependencies not installed. Please run 'pip install -r requirements.txt'"
    exit 1
fi

# Start the server
echo "🌐 Starting FastMCP server on port 8888..."
echo "📡 Server will be available at: http://localhost:8888"
echo "🔧 MCP endpoint: http://localhost:8888/mcp"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

uvicorn main:app --port 8888 --reload --host 0.0.0.0



