# WhatsApp NLP Query Setup Guide

## 🚀 **Overview**

This guide will help you set up WhatsApp integration with NLP query capabilities for your expense management system. Users can ask natural language questions about their expenses via WhatsApp and get intelligent responses.

## 📱 **WhatsApp Integration Options**

### **Option 1: WhatsApp Business API (Recommended for Production)**

#### **1.1 Setup WhatsApp Business Account**
1. Go to [WhatsApp Business API](https://business.whatsapp.com/)
2. Create a business account
3. Verify your business phone number
4. Get your API credentials

#### **1.2 Configure Webhook**
```bash
# Your n8n webhook URL will be:
https://your-n8n-domain.com/webhook/whatsapp-nlp-webhook
```

#### **1.3 Set Webhook in WhatsApp**
```bash
curl -X POST "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "RECIPIENT_PHONE_NUMBER",
    "type": "text",
    "text": {
      "body": "Hello! Ask me about your expenses."
    }
  }'
```

### **Option 2: WhatsApp Webhook Testing (Development)**

#### **2.1 Use ngrok for Local Testing**
```bash
# Install ngrok
npm install -g ngrok

# Expose your n8n webhook
ngrok http 5678

# Your webhook URL will be:
https://your-ngrok-url.ngrok.io/webhook/whatsapp-nlp-webhook
```

#### **2.2 Test with Postman**
```json
POST https://your-ngrok-url.ngrok.io/webhook/whatsapp-nlp-webhook
Content-Type: application/json

{
  "body": {
    "message": {
      "text": "How much did I spend in January?",
      "from": "user123",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

## 🔧 **n8n Workflow Configuration**

### **1. Import Updated Workflow**
1. Open n8n at `http://localhost:5678`
2. Go to Workflows
3. Import the updated `n8n-workflows/expense-automation.json`
4. The workflow now includes WhatsApp NLP query nodes

### **2. Configure WhatsApp Webhook**
1. Click on "WhatsApp Webhook" node
2. Copy the webhook URL
3. Use this URL in your WhatsApp Business API setup

### **3. Configure Credentials**
Ensure these credentials are set up:
- ✅ **OpenRouter API** - For AI processing
- ✅ **Supabase** - For database queries
- ✅ **Prompt Manager** - For NLP prompts

### **4. Test the Workflow**
1. Send a test message to your webhook
2. Check the execution logs
3. Verify the response format

## 📝 **NLP Query Examples**

### **Summary Queries**
```
"How much did I spend in January?"
"What's my total spending this year?"
"Show me my average daily spending"
"How many transactions do I have?"
```

### **List Queries**
```
"Show me my recent expenses"
"List all food expenses"
"Show me Amazon purchases"
"What did I spend on yesterday?"
```

### **Trend Queries**
```
"What are my spending trends?"
"Which category has highest expenses?"
"Show me payment method usage"
"Compare this month vs last month"
```

## 🔄 **Workflow Flow**

### **1. WhatsApp Message Received**
```
WhatsApp → n8n Webhook → WhatsApp Query Filter
```

### **2. NLP Processing**
```
Get NLP Prompt → AI Query Processing → Parse Response
```

### **3. Database Query**
```
SQL Query Check → Execute SQL Query → Format Response
```

### **4. Response**
```
WhatsApp Response → Log Query → Send to User
```

## 📊 **Response Format Examples**

### **Summary Response**
```
📊 Your spending summary for January 2024

💰 Total Amount: ₹45,250
📝 Transactions: 23
📈 Average: ₹1,967
```

### **List Response**
```
📋 Your recent food expenses

1. Swiggy - ₹450
   📅 2024-01-15

2. Domino's Pizza - ₹299
   📅 2024-01-14

3. Starbucks - ₹180
   📅 2024-01-13

... and 7 more transactions
```

### **Trend Response**
```
📈 Your spending trends by category

📊 food_dining: ₹12,450
📊 transportation: ₹8,200
📊 shopping: ₹15,600
📊 utilities: ₹4,800
```

## 🛠️ **Configuration Options**

### **1. User Authentication**
Currently uses a default UUID. For production:
```javascript
// In the workflow, modify user_id mapping
"user_id": "={{ $('WhatsApp Webhook').first().json.body.message.from }}"
```

### **2. Response Formatting**
Customize the response format in "Format WhatsApp Response" node:
```javascript
// Add more emojis, formatting, or custom logic
responseText = `💰 ${queryData.explanation}\n\n`;
```

### **3. Query Limits**
Modify SQL queries to limit results:
```sql
-- Add LIMIT clause for list queries
SELECT * FROM expenses WHERE user_id = 'user123' 
ORDER BY transaction_date DESC LIMIT 10;
```

## 🔍 **Monitoring & Debugging**

### **1. Check Query Logs**
```sql
-- View NLP query logs
SELECT * FROM nlp_query_logs 
WHERE user_id = 'user123' 
ORDER BY created_at DESC;
```

### **2. Monitor Performance**
```sql
-- Check processing times
SELECT 
    AVG(processing_time_ms) as avg_time,
    COUNT(*) as total_queries
FROM nlp_query_logs 
WHERE created_at > NOW() - INTERVAL '1 day';
```

### **3. Error Tracking**
```sql
-- Find failed queries
SELECT * FROM nlp_query_logs 
WHERE query_type = 'error' 
ORDER BY created_at DESC;
```

## 🚨 **Security Considerations**

### **1. Webhook Security**
- Use HTTPS for all webhook URLs
- Implement webhook signature verification
- Rate limit incoming requests

### **2. User Authentication**
- Map WhatsApp numbers to user IDs
- Implement proper user verification
- Use Supabase RLS policies

### **3. SQL Injection Prevention**
- The AI generates parameterized queries
- Validate all user inputs
- Use proper database permissions

## 📈 **Performance Optimization**

### **1. Caching**
- Cache frequently asked queries
- Store user preferences
- Cache database results

### **2. Query Optimization**
- Use database indexes
- Limit result sets
- Optimize SQL queries

### **3. Response Time**
- Target < 3 seconds response time
- Use async processing for complex queries
- Implement request queuing

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Webhook Not Receiving Messages**
- Check webhook URL is correct
- Verify HTTPS is enabled
- Check n8n is running

#### **2. AI Not Understanding Queries**
- Review the NLP prompt
- Check OpenRouter API key
- Monitor AI response logs

#### **3. Database Query Errors**
- Verify Supabase credentials
- Check SQL query syntax
- Monitor database logs

#### **4. Slow Response Times**
- Check database performance
- Monitor AI API response times
- Optimize workflow nodes

### **Debug Commands**
```bash
# Check n8n logs
docker-compose logs n8n

# Test webhook locally
curl -X POST http://localhost:5678/webhook/whatsapp-nlp-webhook \
  -H "Content-Type: application/json" \
  -d '{"body":{"message":{"text":"test","from":"user123"}}}'

# Check Supabase connection
curl -X GET "https://your-project.supabase.co/rest/v1/expenses?select=count" \
  -H "apikey: YOUR_SUPABASE_KEY"
```

## 🎯 **Next Steps**

1. **Set up WhatsApp Business API** or use ngrok for testing
2. **Configure the webhook URL** in your WhatsApp setup
3. **Test with sample queries** to verify functionality
4. **Monitor performance** and optimize as needed
5. **Implement user authentication** for production use

Your WhatsApp NLP query system is now ready to provide intelligent expense insights via natural language conversations!
