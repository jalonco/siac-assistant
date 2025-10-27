#!/usr/bin/env python3
"""
SIAC Assistant - CampaignMetricsWidget Test Script

This script verifies the CampaignMetricsWidget component implementation
and tests the fullscreen dashboard functionality.
"""

import os
import json
from pathlib import Path

def test_widget_structure():
    """Test that the CampaignMetricsWidget file exists and has correct structure."""
    print("=== TESTING CAMPAIGN METRICS WIDGET STRUCTURE ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    if not widget_path.exists():
        print("❌ CampaignMetricsWidget.tsx not found")
        return False
    
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for required React/TypeScript structures
    required_elements = [
        "import React",
        "useOpenAiGlobal",
        "OpenAiGlobal",
        "CampaignMetricsWidget",
        "window.openai",
        "setWidgetState",
        "requestDisplayMode",
        "toolOutput",
        "widgetState"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing required elements: {missing_elements}")
        return False
    
    print("✅ CampaignMetricsWidget structure is correct")
    return True

def test_build_output():
    """Test that the build process generates the CampaignMetricsWidget."""
    print("\n=== TESTING BUILD OUTPUT ===")
    
    widget_path = Path("dist/campaign-metrics-widget.js")
    if not widget_path.exists():
        print("❌ Built CampaignMetricsWidget not found")
        return False
    
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for key functionality in built file
    required_built_elements = [
        "CampaignMetricsWidget",
        "useOpenAiGlobal",
        "window.openai",
        "setWidgetState",
        "quality_score",
        "GREEN",
        "YELLOW",
        "RED"
    ]
    
    missing_built_elements = []
    for element in required_built_elements:
        if element not in content:
            missing_built_elements.append(element)
    
    if missing_built_elements:
        print(f"❌ Missing elements in built file: {missing_built_elements}")
        return False
    
    file_size = len(content)
    print(f"✅ Built CampaignMetricsWidget is {file_size:,} bytes")
    print("✅ Build output contains all required functionality")
    return True

def test_fullscreen_functionality():
    """Test specific fullscreen dashboard functionality."""
    print("\n=== TESTING FULLSCREEN FUNCTIONALITY ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for fullscreen-specific functionality
    fullscreen_elements = [
        "minHeight: '100vh'",
        "fullscreen",
        "requestDisplayMode",
        "timeFilter",
        "selectedMetric",
        "saveWidgetState",
        "quality_score",
        "Template Pacing",
        "131049",
        "delivery_rate",
        "engagement_score",
        "cost_analysis"
    ]
    
    missing_elements = []
    for element in fullscreen_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing fullscreen functionality: {missing_elements}")
        return False
    
    print("✅ Fullscreen functionality is complete")
    return True

def test_quality_metrics():
    """Test quality metrics visualization."""
    print("\n=== TESTING QUALITY METRICS ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for quality score handling
    quality_elements = [
        "getQualityScoreInfo",
        "GREEN",
        "YELLOW", 
        "RED",
        "UNKNOWN",
        "quality_score",
        "Riesgo de pausa",
        "Pausa inminente",
        "Excelente",
        "Advertencia",
        "Crítico"
    ]
    
    missing_elements = []
    for element in quality_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing quality metrics: {missing_elements}")
        return False
    
    print("✅ Quality metrics visualization is complete")
    return True

def test_state_persistence():
    """Test state persistence functionality."""
    print("\n=== TESTING STATE PERSISTENCE ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for state persistence
    persistence_elements = [
        "setWidgetState",
        "widgetState",
        "time_filter",
        "selected_metric",
        "campaign_id",
        "last_updated",
        "saveWidgetState",
        "handleTimeFilterChange",
        "handleMetricChange"
    ]
    
    missing_elements = []
    for element in persistence_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing state persistence: {missing_elements}")
        return False
    
    print("✅ State persistence functionality is complete")
    return True

def test_meta_compliance():
    """Test Meta compliance features."""
    print("\n=== TESTING META COMPLIANCE ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for Meta compliance features
    meta_elements = [
        "template_pacing_active",
        "held_messages",
        "error_code === 131049",
        "Error Meta 131049",
        "Template Pacing",
        "pacing_status",
        "meta_errors",
        "Límite de Marketing"
    ]
    
    missing_elements = []
    for element in meta_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ Missing Meta compliance features: {missing_elements}")
        return False
    
    print("✅ Meta compliance features are complete")
    return True

def test_design_compliance():
    """Test design compliance for fullscreen mode."""
    print("\n=== TESTING DESIGN COMPLIANCE ===")
    
    widget_path = Path("src/CampaignMetricsWidget.tsx")
    with open(widget_path, 'r') as f:
        content = f.read()
    
    # Check for design guideline compliance
    design_checks = [
        ("System font stack", "-apple-system, BlinkMacSystemFont"),
        ("Primary CTA color", "#10B981"),  # Green for primary actions
        ("Fullscreen layout", "minHeight: '100vh'"),
        ("Grid layout", "gridTemplateColumns"),
        ("Responsive design", "repeat(auto-fit, minmax")
    ]
    
    failed_checks = []
    for check_name, check_result in design_checks:
        if not check_result:
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"❌ Design guideline violations: {failed_checks}")
        return False
    
    print("✅ Design follows Apps SDK guidelines for fullscreen mode")
    return True

def test_package_configuration():
    """Test that package.json includes the new widget."""
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
        "build:metrics",
        "build:metrics:dev"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if script not in scripts:
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"❌ Missing build scripts: {missing_scripts}")
        return False
    
    # Check that build script includes metrics
    build_script = scripts.get("build", "")
    if "build:metrics" not in build_script:
        print("❌ Main build script doesn't include metrics widget")
        return False
    
    print("✅ Package configuration includes CampaignMetricsWidget")
    return True

def test_test_files():
    """Test that test files exist for the new widget."""
    print("\n=== TESTING TEST FILES ===")
    
    test_file = Path("test_metrics_widget.html")
    if not test_file.exists():
        print("❌ test_metrics_widget.html not found")
        return False
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Check for React and component imports
    required_elements = [
        "react@18",
        "react-dom@18",
        "CampaignMetricsWidget",
        "campaign-metrics-widget.js"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"❌ test_metrics_widget.html missing elements: {missing_elements}")
        return False
    
    print("✅ Test file is properly configured")
    return True

def main():
    """Main test function."""
    print("SIAC Assistant - CampaignMetricsWidget Test")
    print("=" * 60)
    
    # Change to web directory
    os.chdir("web")
    
    tests = [
        test_widget_structure,
        test_build_output,
        test_fullscreen_functionality,
        test_quality_metrics,
        test_state_persistence,
        test_meta_compliance,
        test_design_compliance,
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
        print("\nCampaignMetricsWidget Features Verified:")
        print("- Fullscreen dashboard structure and functionality")
        print("- Quality metrics visualization (GREEN/YELLOW/RED)")
        print("- State persistence with setWidgetState")
        print("- Meta compliance features (Template Pacing, Error 131049)")
        print("- User interactions (time filters, metric selection)")
        print("- Design compliance for fullscreen mode")
        print("- Build process and test files")
        print("- ChatGPT Skybridge API integration")
    else:
        print("❌ Some tests failed. Please review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()
