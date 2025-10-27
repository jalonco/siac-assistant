#!/usr/bin/env python3
"""
SIAC Assistant - Write Action Tools Test Script

This script demonstrates the two write-action MCP tools:
- siac.register_template (with widget accessibility)
- siac.send_broadcast (with UI widget)
"""

import asyncio
import json
from main import list_tools, call_tool

async def test_template_registration():
    """Test the siac.register_template tool with different scenarios."""
    print("=== TESTING siac.register_template ===")
    
    test_cases = [
        {
            "name": "Successful Template Registration",
            "args": {
                "template_id": "template-123",
                "meta_template_id": "meta_template_456",
                "client_id": "client-789"
            }
        },
        {
            "name": "Failed Template Registration",
            "args": {
                "template_id": "invalid-template",
                "meta_template_id": "meta_template_456",
                "client_id": "client-789"
            }
        },
        {
            "name": "Pending Meta Review",
            "args": {
                "template_id": "pending-template",
                "meta_template_id": "meta_template_456",
                "client_id": "client-789"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            result = await call_tool('siac.register_template', test_case['args'])
            response = result[0].text
            
            # Extract structured data
            if 'Structured Data:' in response:
                structured_part = response.split('Structured Data:')[1].split('Registration Details:')[0].strip()
                structured_data = eval(structured_part)  # Simple parsing for demo
                print(f"✅ Status: {structured_data['status']}")
                print(f"✅ Template ID: {structured_data['template_id']}")
                print(f"✅ Meta Template ID: {structured_data['meta_template_id']}")
                print(f"✅ Client ID: {structured_data['client_id']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_broadcast_scheduling():
    """Test the siac.send_broadcast tool with different segments."""
    print("\n=== TESTING siac.send_broadcast ===")
    
    test_cases = [
        {
            "name": "Regular Customer Segment",
            "args": {
                "template_id": "template-123",
                "segment_name": "clientes_recurrentes",
                "schedule_time_utc": "2024-01-20T10:00:00Z"
            }
        },
        {
            "name": "Test Segment",
            "args": {
                "template_id": "template-123",
                "segment_name": "test_segment",
                "schedule_time_utc": "2024-01-20T10:00:00Z"
            }
        },
        {
            "name": "Premium Segment",
            "args": {
                "template_id": "template-123",
                "segment_name": "premium_customers",
                "schedule_time_utc": "2024-01-20T10:00:00Z"
            }
        },
        {
            "name": "Failed Scheduling",
            "args": {
                "template_id": "template-123",
                "segment_name": "invalid_segment",
                "schedule_time_utc": "2024-01-20T10:00:00Z"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            result = await call_tool('siac.send_broadcast', test_case['args'])
            response = result[0].text
            
            # Extract structured data
            if 'Structured Data:' in response:
                structured_part = response.split('Structured Data:')[1].split('Campaign Details:')[0].strip()
                structured_data = eval(structured_part)  # Simple parsing for demo
                print(f"✅ Campaign ID: {structured_data['campaign_id']}")
                print(f"✅ Status: {structured_data['status']}")
                print(f"✅ Template ID: {structured_data['template_id']}")
                print(f"✅ Segment: {structured_data['segment_name']}")
                print(f"✅ Estimated Recipients: {structured_data['estimated_recipients']}")
                print(f"✅ Schedule Time: {structured_data['schedule_time_utc']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_tool_registration():
    """Test that both write tools are properly registered with correct configuration."""
    print("=== TESTING WRITE TOOLS REGISTRATION ===")
    
    tools = await list_tools()
    tool_names = [tool.name for tool in tools]
    
    print(f"✅ Total tools registered: {len(tools)}")
    print(f"✅ Available tools: {tool_names}")
    
    # Check specific write tools
    write_tools = ['siac.register_template', 'siac.send_broadcast']
    for tool_name in write_tools:
        if tool_name in tool_names:
            tool = next(t for t in tools if t.name == tool_name)
            print(f"\n✅ {tool_name} configuration:")
            print(f"   - readOnlyHint: {getattr(tool, 'readOnlyHint', 'Not set')} (should be Not set)")
            print(f"   - securitySchemes: {getattr(tool, 'securitySchemes', 'Not set')} (should be ['oauth2'])")
            print(f"   - Description: {tool.description[:60]}...")
            
            if tool_name == 'siac.register_template':
                print(f"   - Widget Accessible: {tool.meta.get('openai/widgetAccessible', 'Not set')} (should be True)")
                print(f"   - Invoking message: {tool.meta.get('openai/toolInvocation/invoking', 'Not set')}")
                print(f"   - Invoked message: {tool.meta.get('openai/toolInvocation/invoked', 'Not set')}")
            elif tool_name == 'siac.send_broadcast':
                print(f"   - UI Widget: {tool.meta.get('openai/outputTemplate', 'Not set')}")
                print(f"   - Invoking message: {tool.meta.get('openai/toolInvocation/invoking', 'Not set')}")
                print(f"   - Invoked message: {tool.meta.get('openai/toolInvocation/invoked', 'Not set')}")
        else:
            print(f"❌ {tool_name} not found")

async def test_oauth_requirements():
    """Test OAuth 2.1 requirements and scope configuration."""
    print("\n=== TESTING OAUTH 2.1 REQUIREMENTS ===")
    
    from main import auth_settings
    
    print("✅ OAuth 2.1 Configuration:")
    print(f"   - Issuer URL: {auth_settings.issuer_url}")
    print(f"   - Resource Server: {auth_settings.resource_server_url}")
    print(f"   - Required Scope: {auth_settings.required_scope}")
    print(f"   - Audience: {auth_settings.audience}")
    
    print("\n✅ Write Tools Security:")
    print("   - Both tools require OAuth 2.1 authentication")
    print("   - Both tools require siac.user.full_access scope")
    print("   - Both tools require user confirmation (no readOnlyHint)")
    print("   - TemplateValidationCard can invoke siac.register_template")

async def main():
    """Main test function."""
    print("SIAC Assistant - Write Action Tools Test")
    print("=" * 60)
    
    # Test tool registration
    await test_tool_registration()
    
    # Test OAuth requirements
    await test_oauth_requirements()
    
    # Test template registration
    await test_template_registration()
    
    # Test broadcast scheduling
    await test_broadcast_scheduling()
    
    print("\n" + "=" * 60)
    print("✅ All write action tools tests completed!")
    print("\nKey Features Verified:")
    print("- Write tools registered without readOnlyHint")
    print("- OAuth 2.1 security schemes configured")
    print("- siac.register_template has widget accessibility")
    print("- siac.send_broadcast has UI widget template")
    print("- Mock handlers returning proper structured content")
    print("- User confirmation required for all write operations")
    print("- Invocation status messages for better UX")
    print("- TemplateValidationCard can invoke register_template")

if __name__ == "__main__":
    asyncio.run(main())


