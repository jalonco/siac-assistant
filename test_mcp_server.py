#!/usr/bin/env python3
"""
SIAC Assistant - MCP Endpoint Test Script
This script tests the MCP server endpoint to verify it's working correctly.
"""

import requests
import json
import sys
import time

def test_mcp_endpoint(base_url="http://localhost:8888"):
    """Test the MCP server endpoint."""
    print("🧪 Testing SIAC Assistant MCP Server")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health endpoint responding")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health endpoint error: {e}")
        return False
    
    # Test MCP endpoint
    try:
        print("2. Testing MCP endpoint...")
        mcp_url = f"{base_url}/mcp"
        
        # Test with a simple MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            mcp_url,
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"   ✅ MCP endpoint responding with {len(tools)} tools")
                
                # List available tools
                print("   📋 Available tools:")
                for tool in tools:
                    print(f"      - {tool['name']}")
                
                return True
            else:
                print(f"   ❌ Invalid MCP response format: {data}")
                return False
        else:
            print(f"   ❌ MCP endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ MCP endpoint error: {e}")
        return False

def test_tool_call(base_url="http://localhost:8888"):
    """Test a specific tool call."""
    print("\n3. Testing tool call...")
    
    try:
        mcp_url = f"{base_url}/mcp"
        
        # Test siac.validate_template tool
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "siac.validate_template",
                "arguments": {
                    "template_name": "Test Template",
                    "body_text": "This is a test template with {{1}} variable.",
                    "category": "Marketing",
                    "language_code": "es_ES"
                }
            }
        }
        
        response = requests.post(
            mcp_url,
            json=tool_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "content" in data["result"]:
                print("   ✅ Tool call successful")
                
                # Check for structured content
                content = data["result"]["content"]
                if any("Structured Data:" in item.get("text", "") for item in content):
                    print("   ✅ Response contains structured data")
                else:
                    print("   ⚠️  Response missing structured data")
                
                return True
            else:
                print(f"   ❌ Invalid tool response: {data}")
                return False
        else:
            print(f"   ❌ Tool call failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Tool call error: {e}")
        return False

def main():
    """Main test function."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8888"
    
    print(f"Testing server at: {base_url}")
    print("Make sure the server is running with: ./start.sh")
    print()
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    success = True
    success &= test_mcp_endpoint(base_url)
    success &= test_tool_call(base_url)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Server is ready for ChatGPT integration.")
        print("\nNext steps:")
        print("1. Start ngrok: ngrok http 8888")
        print("2. Launch MCP Inspector: npx @modelcontextprotocol/inspector@latest")
        print("3. Connect Inspector to: http://localhost:8888/mcp")
        print("4. Create ChatGPT connector with ngrok HTTPS URL")
    else:
        print("❌ Some tests failed. Check server logs and try again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())



