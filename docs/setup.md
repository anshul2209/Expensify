# Setup Guide: India-Focused Expense Management System

This guide will help you set up the complete expense management system with Gmail automation, LLM processing, and Supabase database.

## Prerequisites

- n8n instance (self-hosted or cloud)
- Supabase account
- OpenRouter API key
- Gmail account
- Python 3.8+ (for local development)

## 1. Supabase Setup

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note down your project URL and anon key

### 1.2 Run Database Schema

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `supabase/schema.sql`
4. Execute the script to create all tables and data

### 1.3 Configure Row Level Security

The schema includes RLS policies, but you may need to:
1. Enable RLS on all tables
2. Create a user profile in the `users` table
3. Test the policies

## 2. OpenRouter Setup

### 2.1 Get API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up and get your API key
3. Note down the key for n8n configuration

### 2.2 Available Models

The system supports these models through OpenRouter:
- `openai/gpt-4` (recommended)
- `openai/gpt-4-turbo-preview`
- `anthropic/claude-3-sonnet`
- `anthropic/claude-3-haiku`
- `meta-llama/llama-3-70b-instruct`
- `google/gemini-pro`
- `mistralai/mistral-large-latest`

## 3. n8n Setup

### 3.1 Install n8n

```bash
# Using npm
npm install n8n -g

# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### 3.2 Import Workflow

1. Open n8n at `http://localhost:5678`
2. Go to Workflows
3. Click "Import from file"
4. Select `n8n-workflows/expense-automation.json`

### 3.3 Configure Credentials

#### Gmail OAuth2
1. Go to Google Cloud Console
2. Create a new project
3. Enable Gmail API
4. Create OAuth2 credentials
5. Add credentials in n8n:
   - Name: `Gmail OAuth2`
   - Client ID: Your Google OAuth2 Client ID
   - Client Secret: Your Google OAuth2 Client Secret
   - Scope: `https://www.googleapis.com/auth/gmail.readonly`

#### OpenRouter API
1. Add HTTP Header Auth credentials in n8n:
   - Name: `OpenRouter API`
   - Name: `Authorization`
   - Value: `Bearer YOUR_OPENROUTER_API_KEY`

#### Supabase
1. Add Supabase credentials in n8n:
   - Name: `Supabase`
   - URL: Your Supabase project URL
   - Key: Your Supabase anon key

### 3.4 Configure Workflow

1. Update the Gmail trigger:
   - Set polling interval (recommended: every 5 minutes)
   - Configure email filters if needed

2. Update the OpenRouter node:
   - Verify the model is set to `openai/gpt-4`
   - Check the system prompt is loaded correctly

3. Test the workflow:
   - Send a test email with transaction details
   - Check if it's processed correctly

## 4. Python API Setup (Optional)

### 4.1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.2 Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 4.3 Run the API

```bash
python api/expense-api.py
```

## 5. Testing the System

### 5.1 Test Email Types

Send these types of emails to test the system:

#### E-commerce
```
Subject: Amazon Order Confirmation
From: noreply@amazon.in
Content: Your order #123-4567890-1234567 has been confirmed. Total: ₹1,299.00
```

#### Food Delivery
```
Subject: Swiggy Order Confirmation
From: noreply@swiggy.in
Content: Order #SW123456 confirmed. Total: ₹457.90 (including GST ₹19.90)
```

#### Banking
```
Subject: Transaction Alert
From: alerts@hdfcbank.com
Content: ₹500.00 debited from your account via UPI to PhonePe
```

#### Utility Bills
```
Subject: Airtel Bill
From: noreply@airtel.com
Content: Your mobile bill for ₹999.00 is due
```

### 5.2 Verify Data in Supabase

1. Go to your Supabase dashboard
2. Check the `expenses` table
3. Verify the extracted data is correct
4. Check the `email_processing_logs` table for processing status

## 6. Customization

### 6.1 Add Custom Categories

```sql
INSERT INTO categories (name, description, is_default, is_indian_specific, color, icon)
VALUES ('Custom Category', 'Description', FALSE, TRUE, '#FF0000', '🎯');
```

### 6.2 Add Custom Merchants

```sql
INSERT INTO indian_merchants (merchant_name, category, subcategory, is_online, is_offline, city, state)
VALUES ('Your Merchant', 'category_name', 'subcategory', TRUE, FALSE, 'City', 'State');
```

### 6.3 Modify LLM Prompt

Edit `llm/prompts/indian_expense_extraction.txt` to customize:
- Transaction types
- Categories
- Extraction rules
- Output format

## 7. Monitoring and Maintenance

### 7.1 Check Processing Logs

Monitor these tables in Supabase:
- `email_processing_logs`: Email processing status
- `nlp_query_logs`: Query processing logs
- `expenses`: Extracted expense data

### 7.2 Update Exchange Rates

The system uses fallback exchange rates. Update them periodically in `llm/classification.py`.

### 7.3 Model Performance

Monitor which models perform best for your use case:
- Check confidence scores
- Review extraction accuracy
- Switch models if needed

## 8. Troubleshooting

### 8.1 Common Issues

#### Gmail Not Triggering
- Check OAuth2 credentials
- Verify Gmail API is enabled
- Check email filters

#### LLM Not Responding
- Verify OpenRouter API key
- Check API limits
- Try different models

#### Database Errors
- Check Supabase credentials
- Verify RLS policies
- Check table permissions

### 8.2 Debug Mode

Enable debug logging in n8n:
1. Go to Settings
2. Enable "Debug mode"
3. Check execution logs

## 9. Security Considerations

### 9.1 API Keys
- Store API keys securely
- Use environment variables
- Rotate keys regularly

### 9.2 Data Privacy
- Review RLS policies
- Implement data retention
- Consider data encryption

### 9.3 Access Control
- Limit n8n access
- Monitor API usage
- Implement rate limiting

## 10. Scaling

### 10.1 Performance Optimization
- Use connection pooling
- Implement caching
- Optimize database queries

### 10.2 High Availability
- Use n8n cloud or multiple instances
- Implement backup strategies
- Monitor system health

## Support

For issues and questions:
1. Check the logs in Supabase
2. Review n8n execution history
3. Test with sample emails
4. Verify all credentials are correct

The system is designed to be robust and handle various Indian financial transaction patterns. Regular monitoring and updates will ensure optimal performance.
