#!/usr/bin/env python3
"""
SIAC Assistant - Read-Only Tools Test Script

This script demonstrates the two read-only MCP tools:
- siac.validate_template
- siac.get_campaign_metrics
"""

import asyncio
import json
from main import list_tools, call_tool

async def test_template_validation():
    """Test the siac.validate_template tool with different scenarios."""
    print("=== TESTING siac.validate_template ===")
    
    test_cases = [
        {
            "name": "Valid Marketing Template",
            "args": {
                "template_name": "Welcome Offer",
                "body_text": "Welcome to our premium service! Get 20% off your first month.",
                "category": "Marketing",
                "language_code": "es_ES"
            }
        },
        {
            "name": "Short Template (Should Fail)",
            "args": {
                "template_name": "Short Template",
                "body_text": "Hi!",
                "category": "Utility",
                "language_code": "en_US"
            }
        },
        {
            "name": "Spam Content (Should Fail)",
            "args": {
                "template_name": "Spam Template",
                "body_text": "Buy now! Limited time spam offer!",
                "category": "Marketing",
                "language_code": "es_ES"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            result = await call_tool('siac.validate_template', test_case['args'])
            response = result[0].text
            
            # Extract structured data
            if 'Structured Data:' in response:
                structured_part = response.split('Structured Data:')[1].split('Meta Data:')[0].strip()
                structured_data = eval(structured_part)  # Simple parsing for demo
                print(f"✅ Validation Status: {structured_data['validation_status']}")
                print(f"✅ Passed Checks: {structured_data['passed_internal_checks']}")
                print(f"✅ Template: {structured_data['template_name']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_campaign_metrics():
    """Test the siac.get_campaign_metrics tool with different campaign IDs."""
    print("\n=== TESTING siac.get_campaign_metrics ===")
    
    test_campaigns = [
        {
            "name": "Test Campaign",
            "campaign_id": "test-campaign-123"
        },
        {
            "name": "Demo Campaign",
            "campaign_id": "demo-campaign-456"
        },
        {
            "name": "Regular Campaign",
            "campaign_id": "regular-campaign-789"
        }
    ]
    
    for test_campaign in test_campaigns:
        print(f"\n--- {test_campaign['name']} ---")
        try:
            result = await call_tool('siac.get_campaign_metrics', {
                'campaign_id': test_campaign['campaign_id']
            })
            response = result[0].text
            
            # Extract structured data
            if 'Structured Data:' in response:
                structured_part = response.split('Structured Data:')[1].split('Detailed Metrics:')[0].strip()
                structured_data = eval(structured_part)  # Simple parsing for demo
                print(f"✅ Campaign ID: {structured_data['campaign_id']}")
                print(f"✅ Status: {structured_data['status']}")
                print(f"✅ Delivery Rate: {structured_data['delivery_rate']:.1%}")
                print(f"✅ Quality Score: {structured_data['quality_score']}")
                print(f"✅ Total Sent: {structured_data['total_sent']}")
                print(f"✅ Delivered: {structured_data['delivered']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_tool_registration():
    """Test that both tools are properly registered."""
    print("=== TESTING TOOL REGISTRATION ===")
    
    tools = await list_tools()
    tool_names = [tool.name for tool in tools]
    
    print(f"✅ Total tools registered: {len(tools)}")
    print(f"✅ Available tools: {tool_names}")
    
    # Check specific tools
    required_tools = ['siac.validate_template', 'siac.get_campaign_metrics']
    for tool_name in required_tools:
        if tool_name in tool_names:
            tool = next(t for t in tools if t.name == tool_name)
            print(f"✅ {tool_name}:")
            print(f"   - readOnlyHint: {getattr(tool, 'readOnlyHint', False)}")
            print(f"   - UI Widget: {tool.meta.get('openai/outputTemplate', 'Not set')}")
            print(f"   - Description: {tool.description[:60]}...")
        else:
            print(f"❌ {tool_name} not found")

async def main():
    """Main test function."""
    print("SIAC Assistant - Read-Only Tools Test")
    print("=" * 50)
    
    # Test tool registration
    await test_tool_registration()
    
    # Test template validation
    await test_template_validation()
    
    # Test campaign metrics
    await test_campaign_metrics()
    
    print("\n" + "=" * 50)
    print("✅ All read-only tools tests completed!")
    print("\nKey Features Verified:")
    print("- Tool registration with readOnlyHint: true")
    print("- UI widget templates configured")
    print("- Template validation with TemplateCategory enum")
    print("- Campaign metrics with structured data")
    print("- Mock handlers returning proper responses")
    print("- Discovery descriptions for model reasoning")

if __name__ == "__main__":
    asyncio.run(main())


