#!/bin/bash

# FluxLoop Documentation Deployment Script

set -e

echo "🚀 Starting FluxLoop documentation deployment..."

# Check if we're in the website directory
if [ ! -f "docusaurus.config.ts" ]; then
    echo "❌ Error: Must run this script from the website directory"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
npm run clear

# Build the website
echo "🔨 Building website..."
npm run build

# Success message
echo "✅ Build completed successfully!"
echo ""
echo "📦 Static files generated in ./build directory"
echo ""
echo "Next steps:"
echo "  - Test locally: npm run serve"
echo "  - Deploy to GitHub Pages: npm run deploy"
echo "  - Or upload ./build to your hosting provider"
echo ""


