# Expense Management System with n8n Workflow Automation

This project implements an automated expense management system that:
- Monitors Gmail for transaction-related emails
- Uses LLM to parse and classify expenses
- Stores data in Supabase database
- Provides NLP query interface for expense analysis

## Features

- **Gmail Integration**: Automatically detects transaction emails
- **LLM Processing**: Uses OpenRouter + GPT-4 for email parsing and classification
- **Supabase Database**: Stores structured expense data
- **WhatsApp NLP Queries**: Natural language expense queries via WhatsApp
- **AI-Powered Analysis**: Intelligent expense categorization and insights
- **Real-time Processing**: Instant transaction detection and storage

## Architecture

```
Gmail → n8n Workflow → LLM Processing → Supabase → WhatsApp NLP Queries
```

## Setup Instructions

1. **Environment Setup**
   - Install n8n
   - Set up Supabase project
   - Configure OpenAI API
   - Set up Gmail API

2. **Database Setup**
   - Run Supabase migration scripts
   - Configure tables and relationships

3. **n8n Workflow**
   - Import the provided workflow
   - Configure credentials
   - Set up triggers

4. **LLM Integration**
   - Configure OpenAI API key
   - Set up expense classification prompts

## File Structure

```
├── n8n-workflows/
│   └── expense-automation.json          # Main n8n workflow (dynamic prompts)
├── supabase/
│   ├── migrations/
│   ├── functions/
│   └── schema.sql
├── llm/
│   └── prompts/                         # AI prompts for transaction detection & extraction
├── api/
│   └── prompt_manager.py                # FastAPI service for prompt management
├── docs/
│   ├── setup.md                         # Setup instructions
│   ├── prompt-management.md             # Prompt management strategy
│   └── application-flow.md              # Application flow documentation
└── start_prompt_manager.sh              # Script to start prompt manager service
```

## Usage Examples

### WhatsApp NLP Queries
- "How much did I spend in January?"
- "Show me travel expenses for the last 3 months"
- "What are my spending trends?"
- "Which category has the highest expenses?"
- "Show me my recent Amazon purchases"
- "Compare this month vs last month"

### Expense Categories
- Food & Dining
- Transportation
- Shopping
- Travel
- Utilities
- Entertainment
- Healthcare
- Other

## API Endpoints

- `GET /prompts` - List all available prompts
- `GET /prompts/{prompt_type}` - Get specific prompt
- `POST /prompts/reload` - Reload prompts from files
- `POST /webhook/whatsapp-nlp-webhook` - WhatsApp NLP query webhook

## Technologies Used

- **n8n**: Workflow automation
- **OpenRouter**: LLM API gateway
- **Supabase**: Database and real-time features
- **FastAPI**: Prompt management service
- **Gmail API**: Email monitoring
- **WhatsApp Business API**: NLP query interface
