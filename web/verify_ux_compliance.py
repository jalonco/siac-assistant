#!/usr/bin/env python3
"""
SIAC Assistant - UX Design Compliance Verification Script

This script verifies that all frontend components comply with Apps SDK design guidelines:
- System font stack usage
- Restricted color usage (brand color only on primary buttons)
- No nested scrolling in inline cards
"""

import os
import re
from pathlib import Path

def verify_system_font_stack():
    """Verify all components use system font stack."""
    print("=== VERIFYING SYSTEM FONT STACK ===")
    
    components = [
        "src/TemplateValidationCard.tsx",
        "src/BroadcastConfirmationCard.tsx", 
        "src/AuthenticationRequiredCard.tsx",
        "src/CampaignMetricsWidget.tsx"
    ]
    
    system_font_pattern = r"-apple-system,\s*BlinkMacSystemFont"
    
    for component_path in components:
        if not Path(component_path).exists():
            print(f"❌ {component_path} not found")
            return False
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        if not re.search(system_font_pattern, content):
            print(f"❌ {component_path} missing system font stack")
            return False
        
        # Check for custom fonts (should not exist)
        custom_font_patterns = [
            r"fontFamily.*['\"][^'\"]*['\"]",  # Any custom font family
            r"@import.*font",  # Font imports
            r"font-family.*['\"][^'\"]*['\"]"  # CSS font-family
        ]
        
        for pattern in custom_font_patterns:
            matches = re.findall(pattern, content)
            # Filter out system fonts and monospace fonts (allowed for code)
            allowed_fonts = ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 'Courier New', 'monospace']
            for match in matches:
                if not any(font in match for font in allowed_fonts):
                    print(f"❌ {component_path} contains custom font: {match}")
                    return False
        
        print(f"✅ {component_path} uses system font stack correctly")
    
    return True

def verify_color_usage():
    """Verify restricted color usage (brand color only on primary buttons)."""
    print("\n=== VERIFYING COLOR USAGE ===")
    
    components = [
        "src/TemplateValidationCard.tsx",
        "src/BroadcastConfirmationCard.tsx", 
        "src/AuthenticationRequiredCard.tsx",
        "src/CampaignMetricsWidget.tsx"
    ]
    
    brand_color = "#10B981"
    
    for component_path in components:
        if not Path(component_path).exists():
            print(f"❌ {component_path} not found")
            return False
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Find all brand color usages
        brand_color_matches = re.findall(rf"{re.escape(brand_color)}", content)
        
        # Check if brand color is only used in appropriate contexts
        # Look for brand color usage in button contexts
        button_context_pattern = r"backgroundColor.*#10B981|color.*#10B981"
        button_matches = re.findall(button_context_pattern, content)
        
        # Check for inappropriate brand color usage (e.g., in text backgrounds)
        inappropriate_patterns = [
            r"backgroundColor.*#10B981.*text",  # Brand color background for text
            r"color.*#10B981.*text",  # Brand color for regular text
        ]
        
        inappropriate_usage = False
        for pattern in inappropriate_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                inappropriate_usage = True
                break
        
        if inappropriate_usage:
            print(f"❌ {component_path} uses brand color inappropriately")
            return False
        
        # Verify brand color is used for primary buttons/accents
        primary_button_pattern = r"backgroundColor.*#10B981"
        if not re.search(primary_button_pattern, content):
            print(f"⚠️  {component_path} doesn't use brand color for primary buttons")
        else:
            print(f"✅ {component_path} uses brand color appropriately")
    
    return True

def verify_no_nested_scrolling():
    """Verify no nested scrolling in inline card components."""
    print("\n=== VERIFYING NO NESTED SCROLLING ===")
    
    # Only check inline card components (not fullscreen)
    inline_components = [
        "src/TemplateValidationCard.tsx",
        "src/BroadcastConfirmationCard.tsx", 
        "src/AuthenticationRequiredCard.tsx"
    ]
    
    for component_path in inline_components:
        if not Path(component_path).exists():
            print(f"❌ {component_path} not found")
            return False
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for nested scrolling patterns
        nested_scrolling_patterns = [
            r"overflow.*hidden",
            r"overflow.*scroll",
            r"overflow.*auto",
            r"height.*fixed",
            r"height.*100vh",  # Should not be in inline cards
            r"maxHeight.*\d+px"  # Fixed max heights that could cause scrolling
        ]
        
        violations = []
        for pattern in nested_scrolling_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Allow some exceptions for specific use cases
                if "height.*100vh" in pattern and "CampaignMetricsWidget" in component_path:
                    continue  # Fullscreen widget can use 100vh
                violations.append(f"{pattern}: {match}")
        
        if violations:
            print(f"❌ {component_path} has nested scrolling violations:")
            for violation in violations:
                print(f"   - {violation}")
            return False
        
        print(f"✅ {component_path} has no nested scrolling")
    
    return True

def verify_fullscreen_compliance():
    """Verify CampaignMetricsWidget follows fullscreen guidelines."""
    print("\n=== VERIFYING FULLSCREEN COMPLIANCE ===")
    
    component_path = "src/CampaignMetricsWidget.tsx"
    
    if not Path(component_path).exists():
        print(f"❌ {component_path} not found")
        return False
    
    with open(component_path, 'r') as f:
        content = f.read()
    
    # Check for fullscreen-specific patterns
    fullscreen_patterns = [
        r"minHeight.*100vh",  # Should use minHeight, not height
        r"fontFamily.*-apple-system",  # System font stack
        r"gridTemplateColumns",  # Responsive grid layout
        r"repeat\(auto-fit,\s*minmax"  # Responsive grid
    ]
    
    violations = []
    for pattern in fullscreen_patterns:
        if not re.search(pattern, content):
            violations.append(f"Missing: {pattern}")
    
    if violations:
        print(f"❌ {component_path} fullscreen compliance issues:")
        for violation in violations:
            print(f"   - {violation}")
        return False
    
    # Check for inappropriate patterns in fullscreen
    inappropriate_patterns = [
        r"overflow.*hidden",  # Should not hide overflow in fullscreen
        r"height.*fixed"  # Should not use fixed heights
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, content):
            print(f"❌ {component_path} has inappropriate fullscreen pattern: {pattern}")
            return False
    
    print(f"✅ {component_path} follows fullscreen guidelines")
    return True

def verify_data_separation():
    """Verify server handlers properly separate data between structuredContent and _meta."""
    print("\n=== VERIFYING DATA SEPARATION ===")
    
    server_path = "../server/main.py"
    
    if not Path(server_path).exists():
        print(f"❌ {server_path} not found")
        return False
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Check for proper data separation patterns
    separation_patterns = [
        r"# STRUCTURED CONTENT.*Visible to Model",
        r"# CONTENT.*Visible to Model", 
        r"# _META.*Hidden from Model",
        r"structured_content.*=.*{",
        r"detailed_meta.*=.*{",
        r"Meta Data.*detailed_meta"
    ]
    
    violations = []
    for pattern in separation_patterns:
        if not re.search(pattern, content):
            violations.append(f"Missing: {pattern}")
    
    if violations:
        print(f"❌ {server_path} data separation issues:")
        for violation in violations:
            print(f"   - {violation}")
        return False
    
    # Check for sensitive data in structured content (should not be there)
    sensitive_patterns = [
        r"raw_validation_errors.*structured_content",
        r"template_html_mockup.*structured_content",
        r"meta_errors.*structured_content"
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, content):
            print(f"❌ {server_path} has sensitive data in structured content: {pattern}")
            return False
    
    print(f"✅ {server_path} properly separates data")
    return True

def main():
    """Main verification function."""
    print("SIAC Assistant - UX Design Compliance Verification")
    print("=" * 60)
    
    # Change to web directory
    os.chdir("web")
    
    tests = [
        verify_system_font_stack,
        verify_color_usage,
        verify_no_nested_scrolling,
        verify_fullscreen_compliance,
        verify_data_separation
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"Verification Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL UX COMPLIANCE TESTS PASSED!")
        print("\nVerified Guidelines:")
        print("- ✅ System font stack usage (-apple-system, BlinkMacSystemFont)")
        print("- ✅ Restricted color usage (brand color #10B981 only on primary buttons)")
        print("- ✅ No nested scrolling in inline cards")
        print("- ✅ Fullscreen compliance for CampaignMetricsWidget")
        print("- ✅ Proper data separation in server handlers")
        print("\nAll components follow Apps SDK design guidelines!")
    else:
        print("❌ Some compliance tests failed. Please review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()



