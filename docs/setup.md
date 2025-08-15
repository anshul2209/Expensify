# Setup Guide: India-Focused Expense Management System

This guide will help you set up the complete expense management system with Gmail automation, LLM processing, and Supabase database.

## Prerequisites

- n8n instance (self-hosted or cloud)
- Supabase account
- AIML API key
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

## 2. AIML API Setup

### 2.1 Get API Key

1. Go to [aimlapi.com](https://aimlapi.com)
2. Sign up and get your API key
3. Note down the key for n8n configuration

### 2.2 Available Models

The system supports these models through AIML API:
- `gpt-4` (recommended)
- `gpt-3.5-turbo`
- `claude-3-sonnet`
- `claude-3-haiku`
- `gemini-pro`
- `llama-3-70b`

## 3. n8n Setup (Self-Hosted)

### 3.1 Install n8n

#### Option A: Docker (Recommended)
```bash
# Create a directory for n8n data
mkdir -p ~/n8n-data

# Run n8n with Docker
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your_secure_password \
  -e N8N_HOST=localhost \
  -e N8N_PORT=5678 \
  -e N8N_PROTOCOL=http \
  -e WEBHOOK_URL=http://localhost:5678/ \
  --restart unless-stopped \
  n8nio/n8n:latest
```

#### Option B: Docker Compose (Production)
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your_secure_password
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - N8N_ENCRYPTION_KEY=your_32_character_encryption_key
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_password
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    container_name: n8n-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  n8n_data:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

#### Option C: npm (Development)
```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start
```

### 3.2 Access n8n

1. Open your browser and go to `http://localhost:5678`
2. Login with the credentials you set (admin/your_secure_password)
3. You'll see the n8n dashboard

### 3.3 Import the Expense Automation Workflow

1. In n8n dashboard, click **"Workflows"** in the left sidebar
2. Click **"Import from file"** button
3. Select the file: `n8n-workflows/expense-automation.json`
4. Click **"Import"**
5. The workflow will be imported and you can see it in your workflows list

### 3.4 Configure Credentials

#### Gmail OAuth2 Setup
1. **Go to Google Cloud Console**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Gmail API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth2 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "n8n Expense Management"
   - Authorized redirect URIs: `http://localhost:5678/callback`
   - Click "Create"
   - Note down the **Client ID** and **Client Secret**

4. **Add Gmail Credentials in n8n**:
   - In n8n, go to **"Credentials"** in the left sidebar
   - Click **"Add Credential"**
   - Search for "Gmail"
   - Select "Gmail OAuth2 API"
   - Fill in:
     - **Name**: `Gmail OAuth2`
     - **Client ID**: Your Google OAuth2 Client ID
     - **Client Secret**: Your Google OAuth2 Client Secret
     - **Scope**: `https://www.googleapis.com/auth/gmail.readonly`
   - Click **"Save"**
   - Click **"Connect"** and authorize with your Gmail account

#### AIML API Setup
1. **Get AIML API Key**:
   - Visit [AIML API](https://aimlapi.com/)
   - Sign up and get your API key

2. **Add AIML API Credentials in n8n**:
   - In n8n, go to **"Credentials"**
   - Click **"Add Credential"**
   - Search for "HTTP Header Auth"
   - Select "HTTP Header Auth"
   - Fill in:
     - **Name**: `aimlApiKey`
     - **Name**: `Authorization`
     - **Value**: `Bearer YOUR_AIML_API_KEY`
   - Click **"Save"**

#### Supabase Setup
1. **Get Supabase Credentials**:
   - Go to your Supabase project dashboard
   - Go to "Settings" > "API"
   - Copy the **Project URL** and **anon public** key

2. **Add Supabase Credentials in n8n**:
   - In n8n, go to **"Credentials"**
   - Click **"Add Credential"**
   - Search for "Supabase"
   - Select "Supabase"
   - Fill in:
     - **Name**: `Supabase`
     - **URL**: Your Supabase project URL
     - **Key**: Your Supabase anon key
   - Click **"Save"**

### 3.5 Configure the Workflow

1. **Open the Workflow**:
   - Click on the imported "Expense Automation" workflow
   - You'll see the workflow diagram

2. **Configure Gmail Trigger**:
   - Click on the "Gmail Trigger" node
   - In the right panel, configure:
     - **Authentication**: Select your Gmail OAuth2 credential
     - **Resource**: `Message`
     - **Operation**: `Get All`
     - **Return All**: `false`
     - **Limit**: `10`
     - **Additional Fields** > **Format**: `full`

3. **Configure AIML API Nodes**:
   - Click on "AI Transaction Detection" node
   - Verify **Authentication** is set to your AIML API credential
   - Check that **Model** is set to `gpt-4`
   - Repeat for "AI Expense Extraction" node

4. **Configure Supabase Node**:
   - Click on "Save to Supabase" node
   - Set **Authentication** to your Supabase credential
   - Verify the **Table** is set to `expenses`

5. **Set Polling Interval**:
   - In the Gmail Trigger node, you can set how often to check for emails
   - Recommended: Every 5 minutes for testing, every 1 minute for production

### 3.6 Test the Workflow

1. **Activate the Workflow**:
   - Click the **"Active"** toggle in the top right
   - The workflow will start monitoring Gmail

2. **Send Test Email**:
   - Send yourself an email with transaction details
   - Example:
     ```
     Subject: Amazon Order Confirmation
     From: noreply@amazon.in
     Content: Your order #123-4567890-1234567 has been confirmed. Total: ₹1,299.00
     ```

3. **Monitor Execution**:
   - Go to **"Executions"** in the left sidebar
   - You should see the workflow execution
   - Click on it to see detailed logs

### 3.7 Production Considerations

#### Environment Variables
For production, set these environment variables:
```bash
# Security
N8N_ENCRYPTION_KEY=your_32_character_encryption_key
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password

# Database (if using PostgreSQL)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your_postgres_host
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n_user
DB_POSTGRESDB_PASSWORD=n8n_password

# Webhook URL
WEBHOOK_URL=https://your-domain.com/

# Logging
N8N_LOG_LEVEL=info
```

#### Reverse Proxy Setup
For production, use a reverse proxy (nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### SSL Certificate
Use Let's Encrypt for free SSL:
```bash
sudo certbot --nginx -d your-domain.com
```

## 4. Prompt Manager Setup (Optional)

### 4.1 Install Dependencies

```bash
pip install fastapi uvicorn
```

### 4.2 Start Prompt Manager Service

```bash
./start_prompt_manager.sh
```

This starts the FastAPI service on `http://localhost:8001` for managing AI prompts.

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

The system uses fallback exchange rates. Update them periodically in the n8n workflow if needed.

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
- Verify AIML API key
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
