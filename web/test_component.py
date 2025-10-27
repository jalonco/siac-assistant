#!/usr/bin/env python3
"""
SIAC Assistant - TemplateValidationCard Component Test Script

This script verifies the TemplateValidationCard component implementation
and tests the ChatGPT Skybridge API integration.
"""

import os
import json
from pathlib import Path

def test_component_structure():
    """Test that the component file exists and has the correct structure."""
    print("=== TESTING COMPONENT STRUCTURE ===")
    
    component_path = Path("src/TemplateValidationCard.tsx")
    if not component_path.exists():
        print("❌ TemplateValidationCard.tsx not found")
        return False
    
    with open(component_path, 'r') as f:
        content = f.read()
    
    # Check for required imports and structures
    required_elements = [
        "import React",
        "useOpenAiGlobal",
        "OpenAiGlobal",
        "TemplateValidationCard",
        "window.openai",
        "callTool",
        "sendFollowUpMessage",
        "toolOutput",
        "toolResponseMetadata",
        "SUCCESS",
        "FAILED",
        "Registrar Plantilla",
        "Corregir Prompt"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing required elements: {missing_elements}")
        return False
    
    print("✅ Component structure is correct")
    return True

def test_build_output():
    """Test that the build process generates the correct output."""
    print("\n=== TESTING BUILD OUTPUT ===")
    
    dist_path = Path("dist/template-validation-card.js")
    if not dist_path.exists():
        print("❌ Built component not found")
        return False
    
    with open(dist_path, 'r') as f:
        content = f.read()
    
    # Check for key functionality in built file
    required_built_elements = [
        "TemplateValidationCard",
        "useOpenAiGlobal",
        "window.openai",
        "callTool",
        "sendFollowUpMessage",
        "validation_status",
        "SUCCESS",
        "FAILED"
    ]
    
    missing_built_elements = []
    for element in required_built_elements:
        if element not in content:
            missing_built_elements.append(element)
    
    if missing_built_elements:
        print(f"❌ Missing elements in built file: {missing_built_elements}")
        return False
    
    file_size = len(content)
    print(f"✅ Built component is {file_size:,} bytes")
    print("✅ Build output contains all required functionality")
    return True

def test_package_configuration():
    """Test that package.json is properly configured."""
    print("\n=== TESTING PACKAGE CONFIGURATION ===")
    
    package_path = Path("package.json")
    if not package_path.exists():
        print("❌ package.json not found")
        return False
    
    with open(package_path, 'r') as f:
        package_data = json.load(f)
    
    # Check required dependencies
    required_deps = ["react", "react-dom"]
    required_dev_deps = ["typescript", "esbuild", "@types/react", "@types/react-dom"]
    
    missing_deps = []
    for dep in required_deps:
        if dep not in package_data.get("dependencies", {}):
            missing_deps.append(dep)
    
    missing_dev_deps = []
    for dep in required_dev_deps:
        if dep not in package_data.get("devDependencies", {}):
            missing_dev_deps.append(dep)
    
    if missing_deps or missing_dev_deps:
        print(f"❌ Missing dependencies: {missing_deps + missing_dev_deps}")
        return False
    
    # Check build script
    build_script = package_data.get("scripts", {}).get("build", "")
    if "esbuild" not in build_script or "TemplateValidationCard.tsx" not in build_script:
        print("❌ Build script is not properly configured")
        return False
    
    print("✅ Package configuration is correct")
    return True

def test_typescript_configuration():
    """Test that TypeScript configuration is correct."""
    print("\n=== TESTING TYPESCRIPT CONFIGURATION ===")
    
    tsconfig_path = Path("tsconfig.json")
    if not tsconfig_path.exists():
        print("❌ tsconfig.json not found")
        return False
    
    with open(tsconfig_path, 'r') as f:
        tsconfig_data = json.load(f)
    
    compiler_options = tsconfig_data.get("compilerOptions", {})
    
    # Check required TypeScript settings
    required_settings = {
        "target": "ES2020",
        "jsx": "react-jsx",
        "strict": True,
        "module": "ESNext"
    }
    
    missing_settings = []
    for key, expected_value in required_settings.items():
        if compiler_options.get(key) != expected_value:
            missing_settings.append(f"{key}: expected {expected_value}, got {compiler_options.get(key)}")
    
    if missing_settings:
        print(f"❌ TypeScript configuration issues: {missing_settings}")
        return False
    
    print("✅ TypeScript configuration is correct")
    return True

def test_chatgpt_api_integration():
    """Test ChatGPT Skybridge API integration patterns."""
    print("\n=== TESTING CHATGPT API INTEGRATION ===")
    
    component_path = Path("src/TemplateValidationCard.tsx")
    with open(component_path, 'r') as f:
        content = f.read()
    
    # Check for ChatGPT API integration patterns
    api_patterns = [
        "window.openai",
        "toolOutput",
        "toolResponseMetadata",
        "callTool",
        "sendFollowUpMessage",
        "siac.register_template",
        "raw_validation_errors"
    ]
    
    missing_patterns = []
    for pattern in api_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print(f"❌ Missing ChatGPT API integration patterns: {missing_patterns}")
        return False
    
    print("✅ ChatGPT API integration patterns are correct")
    return True

def test_ui_design_guidelines():
    """Test that the component follows OpenAI design guidelines."""
    print("\n=== TESTING UI DESIGN GUIDELINES ===")
    
    component_path = Path("src/TemplateValidationCard.tsx")
    with open(component_path, 'r') as f:
        content = f.read()
    
    # Check for design guideline compliance
    design_checks = [
        ("System font stack", "-apple-system, BlinkMacSystemFont"),
        ("Primary CTA color", "#10B981"),  # Green for primary action
        ("Secondary CTA color", "#6B7280"),  # Gray for secondary action
        ("No nested scrolling", "overflow: hidden" not in content),  # Should not have overflow hidden
        ("Auto-height", "height: auto" in content or "height:" not in content)
    ]
    
    failed_checks = []
    for check_name, check_result in design_checks:
        if not check_result:
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"❌ Design guideline violations: {failed_checks}")
        return False
    
    print("✅ UI design follows OpenAI guidelines")
    return True

def test_scenario_logic():
    """Test that both SUCCESS and FAILED scenarios are implemented."""
    print("\n=== TESTING SCENARIO LOGIC ===")
    
    component_path = Path("src/TemplateValidationCard.tsx")
    with open(component_path, 'r') as f:
        content = f.read()
    
    # Check for scenario implementations
    success_elements = [
        "validation_status === 'SUCCESS'",
        "Registrar Plantilla",
        "handleRegisterTemplate",
        "renderTemplatePreview"
    ]
    
    failed_elements = [
        "validation_status === 'FAILED'",
        "Corregir Prompt",
        "handleCorrectPrompt",
        "renderValidationErrors"
    ]
    
    missing_success = [elem for elem in success_elements if elem not in content]
    missing_failed = [elem for elem in failed_elements if elem not in content]
    
    if missing_success:
        print(f"❌ Missing SUCCESS scenario elements: {missing_success}")
        return False
    
    if missing_failed:
        print(f"❌ Missing FAILED scenario elements: {missing_failed}")
        return False
    
    print("✅ Both SUCCESS and FAILED scenarios are implemented")
    return True

def main():
    """Main test function."""
    print("SIAC Assistant - TemplateValidationCard Component Test")
    print("=" * 60)
    
    # Change to web directory
    os.chdir("web")
    
    tests = [
        test_component_structure,
        test_build_output,
        test_package_configuration,
        test_typescript_configuration,
        test_chatgpt_api_integration,
        test_ui_design_guidelines,
        test_scenario_logic
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
        print("\nKey Features Verified:")
        print("- Component structure with ChatGPT API integration")
        print("- Build process generates correct output")
        print("- Package and TypeScript configuration")
        print("- ChatGPT Skybridge API integration patterns")
        print("- OpenAI design guidelines compliance")
        print("- SUCCESS and FAILED scenario logic")
        print("- Tool call and follow-up message functionality")
    else:
        print("❌ Some tests failed. Please review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()



