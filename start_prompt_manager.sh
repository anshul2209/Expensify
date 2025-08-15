#!/bin/bash

# Start Prompt Manager Service
# This script starts the FastAPI prompt manager service

echo "🚀 Starting Prompt Manager Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "📦 Installing required packages..."
    pip3 install fastapi uvicorn
}

# Check if prompt files exist
if [ ! -f "llm/prompts/transaction_detection.txt" ]; then
    echo "❌ Prompt file not found: llm/prompts/transaction_detection.txt"
    exit 1
fi

if [ ! -f "llm/prompts/indian_expense_extraction.txt" ]; then
    echo "❌ Prompt file not found: llm/prompts/indian_expense_extraction.txt"
    exit 1
fi

# Start the service
echo "🌐 Starting Prompt Manager API on http://localhost:8001"
echo "📚 Available endpoints:"
echo "   - GET  /prompts (list all prompts)"
echo "   - GET  /prompts/{prompt_type} (get specific prompt)"
echo "   - POST /prompts/reload (reload prompts from files)"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

cd "$(dirname "$0")"
python3 api/prompt_manager.py
