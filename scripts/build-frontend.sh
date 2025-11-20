#!/bin/bash

# Build script for Hotel Booking System Frontend
# This script builds the React TypeScript frontend for production

set -e

echo "🏗️  Building Hotel Booking System Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf dist/

# Build the application
echo "🔨 Building application..."
npm run build

# Check if build was successful
if [ -d "dist" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Build output is in: $(pwd)/dist"
    
    # Show build size
    echo "📊 Build size:"
    du -sh dist/
    
    # List main files
    echo "📄 Main files:"
    ls -la dist/
    
else
    echo "❌ Build failed!"
    exit 1
fi

echo "🎉 Frontend build complete!"
