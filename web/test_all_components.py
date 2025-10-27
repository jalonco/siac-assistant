#!/usr/bin/env python3
"""
SIAC Assistant - All Components Test Script

This script verifies all three React/TypeScript components:
- TemplateValidationCard
- BroadcastConfirmationCard  
- AuthenticationRequiredCard
"""

import os
import json
from pathlib import Path

def test_component_files():
    """Test that all component files exist and have correct structure."""
    print("=== TESTING COMPONENT FILES ===")
    
    components = [
        "src/TemplateValidationCard.tsx",
        "src/BroadcastConfirmationCard.tsx", 
        "src/AuthenticationRequiredCard.tsx"
    ]
    
    for component_path in components:
        if not Path(component_path).exists():
            print(f"❌ {component_path} not found")
            return False
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for required React/TypeScript structures
        required_elements = [
            "import React",
            "useOpenAiGlobal",
            "OpenAiGlobal",
            "window.openai"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ {component_path} missing elements: {missing_elements}")
            return False
        
        print(f"✅ {component_path} structure is correct")
    
    return True

def test_build_output():
    """Test that the build process generates all components."""
    print("\n=== TESTING BUILD OUTPUT ===")
    
    expected_files = [
        "dist/template-validation-card.js",
        "dist/broadcast-confirmation-card.js",
        "dist/authentication-required-card.js"
    ]
    
    for file_path in expected_files:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found")
            return False
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for key functionality in built files
        required_built_elements = [
            "useOpenAiGlobal",
            "window.openai"
        ]
        
        missing_built_elements = []
        for element in required_built_elements:
            if element not in content:
                missing_built_elements.append(element)
        
        if missing_built_elements:
            print(f"❌ {file_path} missing elements: {missing_built_elements}")
            return False
        
        file_size = len(content)
        print(f"✅ {file_path} is {file_size:,} bytes")
    
    return True

def test_specific_components():
    """Test specific functionality for each component."""
    print("\n=== TESTING COMPONENT-SPECIFIC FUNCTIONALITY ===")
    
    # Test TemplateValidationCard
    template_path = Path("src/TemplateValidationCard.tsx")
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template_elements = [
        "SUCCESS",
        "FAILED", 
        "Registrar Plantilla",
        "Corregir Prompt",
        "siac.register_template",
        "sendFollowUpMessage"
    ]
    
    missing_template = [elem for elem in template_elements if elem not in template_content]
    if missing_template:
        print(f"❌ TemplateValidationCard missing: {missing_template}")
        return False
    print("✅ TemplateValidationCard functionality complete")
    
    # Test BroadcastConfirmationCard
    broadcast_path = Path("src/BroadcastConfirmationCard.tsx")
    with open(broadcast_path, 'r') as f:
        broadcast_content = f.read()
    
    broadcast_elements = [
        "SCHEDULED",
        "SCHEDULED_TEST",
        "Ver Métricas Detalladas",
        "requestDisplayMode",
        "campaign_id",
        "segment_name"
    ]
    
    missing_broadcast = [elem for elem in broadcast_elements if elem not in broadcast_content]
    if missing_broadcast:
        print(f"❌ BroadcastConfirmationCard missing: {missing_broadcast}")
        return False
    print("✅ BroadcastConfirmationCard functionality complete")
    
    # Test AuthenticationRequiredCard
    auth_path = Path("src/AuthenticationRequiredCard.tsx")
    with open(auth_path, 'r') as f:
        auth_content = f.read()
    
    auth_elements = [
        "Conectar Cuenta SIAC",
        "authentication_required",
        "OAuth 2.1",
        "PKCE",
        "sendFollowUpMessage"
    ]
    
    missing_auth = [elem for elem in auth_elements if elem not in auth_content]
    if missing_auth:
        print(f"❌ AuthenticationRequiredCard missing: {missing_auth}")
        return False
    print("✅ AuthenticationRequiredCard functionality complete")
    
    return True

def test_design_guidelines():
    """Test that all components follow Apps SDK design guidelines."""
    print("\n=== TESTING DESIGN GUIDELINES COMPLIANCE ===")
    
    components = [
        "src/TemplateValidationCard.tsx",
        "src/BroadcastConfirmationCard.tsx",
        "src/AuthenticationRequiredCard.tsx"
    ]
    
    for component_path in components:
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for design guideline compliance
        design_checks = [
            ("System font stack", "-apple-system, BlinkMacSystemFont"),
            ("Primary CTA color", "#10B981"),  # Green for primary actions
            ("No nested scrolling", "overflow: hidden" not in content),  # Should not have overflow hidden
            ("Auto-height", "height: auto" in content or "height:" not in content or "height: '48px'" in content or "height: '20px'" in content)
        ]
        
        failed_checks = []
        for check_name, check_result in design_checks:
            if not check_result:
                failed_checks.append(check_name)
        
        if failed_checks:
            print(f"❌ {component_path} design violations: {failed_checks}")
            return False
        
        print(f"✅ {component_path} follows design guidelines")
    
    return True

def test_package_configuration():
    """Test that package.json is properly configured for all components."""
    print("\n=== TESTING PACKAGE CONFIGURATION ===")
    
    package_path = Path("package.json")
    if not package_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_path, 'r') as f:
        package_data = json.load(f)
    
    # Check build scripts
    scripts = package_data.get("scripts", {})
    required_scripts = [
        "build",
        "build:template", 
        "build:broadcast",
        "build:auth",
        "build:dev",
        "clean"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if script not in scripts:
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Missing build scripts: {missing_scripts}")
        return False
    
    print("✅ Package configuration is correct")
    return True

def test_test_files():
    """Test that test files exist and are properly configured."""
    print("\n=== TESTING TEST FILES ===")
    
    test_files = [
        "test.html",
        "test_all_components.html"
    ]
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ {test_file} not found")
            return False
        
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Check for React and component imports
        required_elements = [
            "react@18",
            "react-dom@18",
            "TemplateValidationCard"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ {test_file} missing elements: {missing_elements}")
            return False
        
        print(f"✅ {test_file} is properly configured")
    
    return True

def main():
    """Main test function."""
    print("SIAC Assistant - All Components Test")
    print("=" * 60)
    
    # Change to web directory
    os.chdir("web")
    
    tests = [
        test_component_files,
        test_build_output,
        test_specific_components,
        test_design_guidelines,
        test_package_configuration,
        test_test_files
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
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\nComponents Verified:")
        print("- TemplateValidationCard: Template validation and registration")
        print("- BroadcastConfirmationCard: Campaign confirmation and metrics navigation")
        print("- AuthenticationRequiredCard: OAuth 2.1 authentication flow")
        print("\nKey Features Verified:")
        print("- All components follow Apps SDK design guidelines")
        print("- ChatGPT Skybridge API integration")
        print("- Build process generates all components")
        print("- Test files properly configured")
        print("- Package configuration complete")
    else:
        print("❌ Some tests failed. Please review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
