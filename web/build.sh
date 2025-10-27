#!/bin/bash
# SIAC Assistant - Frontend Build Script
# This script builds the React/TypeScript components for ChatGPT Skybridge

echo "🎨 Building SIAC Assistant Frontend Components..."
echo "================================================"

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the web/ directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
npm run clean

# Build the components
echo "🔨 Building components..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Output: dist/template-validation-card.js"
    
    # Show file size
    if [ -f "dist/template-validation-card.js" ]; then
        size=$(wc -c < "dist/template-validation-card.js")
        echo "📊 Bundle size: $size bytes"
    fi
    
    echo ""
    echo "🧪 To test locally:"
    echo "   open test.html"
    echo ""
    echo "🔗 For ChatGPT integration:"
    echo "   Serve dist/template-validation-card.js via HTTPS"
else
    echo "❌ Build failed!"
    exit 1
fi



