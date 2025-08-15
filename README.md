# Expense Management System with n8n Workflow Automation

This project implements an automated expense management system that:
- Monitors Gmail for transaction-related emails
- Uses LLM to parse and classify expenses
- Stores data in Supabase database
- Provides NLP query interface for expense analysis

## Features

- **Gmail Integration**: Automatically detects transaction emails
- **LLM Processing**: Uses OpenAI GPT for email parsing and expense classification
- **Supabase Database**: Stores structured expense data
- **NLP Queries**: Natural language expense analysis and reporting
- **Categories**: Automatic expense categorization
- **Trends**: Spending pattern analysis

## Architecture

```
Gmail → n8n Workflow → LLM Processing → Supabase → NLP Query Interface
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
│   ├── expense-automation.json
│   └── nlp-query-workflow.json
├── supabase/
│   ├── migrations/
│   ├── functions/
│   └── schema.sql
├── llm/
│   ├── prompts/
│   └── classification.py
├── api/
│   ├── expense-api.py
│   └── nlp-query.py
└── docs/
    ├── setup.md
    └── api-reference.md
```

## Usage Examples

### NLP Queries
- "How much did I spend in January?"
- "Show me travel expenses for the last 3 months"
- "What are my spending trends?"
- "Which category has the highest expenses?"

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

- `POST /api/expenses` - Add expense manually
- `GET /api/expenses` - List expenses with filters
- `POST /api/query` - NLP query interface
- `GET /api/analytics` - Spending analytics

## Technologies Used

- **n8n**: Workflow automation
- **OpenAI GPT**: Email parsing and classification
- **Supabase**: Database and real-time features
- **Python**: API and LLM integration
- **Gmail API**: Email monitoring
