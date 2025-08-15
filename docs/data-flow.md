# Data Flow: Expense Management System

## 🔄 **Complete Data Flow Overview**

```
Gmail Email → AI Transaction Detection → AI Expense Extraction → Data Parsing → Supabase Storage → Logging
```

## 📊 **Data Storage in Supabase**

### **1. Main Data Tables**

#### **A. `expenses` Table - Primary Transaction Data**
```sql
CREATE TABLE expenses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'INR',
    description TEXT NOT NULL,
    category expense_category NOT NULL,
    merchant TEXT,
    transaction_date DATE NOT NULL,
    payment_method payment_method,
    city TEXT,
    state TEXT,
    gst_amount DECIMAL(10,2),
    gst_percentage DECIMAL(5,2),
    confidence_score DECIMAL(3,2),
    email_subject TEXT,
    email_sender TEXT,
    email_source TEXT,
    raw_email_content TEXT,
    parsed_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Data Mapping from n8n Workflow:**
- `user_id` → Gmail user ID (or default UUID)
- `amount` → Extracted amount from AI
- `currency` → Extracted currency (defaults to INR)
- `description` → AI-generated description
- `category` → AI-categorized expense type
- `merchant` → Extracted merchant name
- `transaction_date` → Extracted date (or current date)
- `payment_method` → UPI, card, etc.
- `city` & `state` → Location data
- `gst_amount` & `gst_percentage` → GST information
- `confidence_score` → AI confidence (0.0-1.0)
- `email_subject` & `email_sender` → Email metadata
- `email_source` → Gmail message ID
- `raw_email_content` → Original email content
- `parsed_data` → Complete AI response as JSON

#### **B. `email_processing_logs` Table - Processing History**
```sql
CREATE TABLE email_processing_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    email_message_id TEXT NOT NULL,
    email_subject TEXT,
    email_sender TEXT,
    processing_status TEXT NOT NULL, -- 'pending', 'processing', 'completed', 'failed', 'skipped'
    llm_response JSONB,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Processing Status Types:**
- `completed` → Successfully processed transaction
- `skipped` → Not a transaction email
- `failed` → Processing error occurred
- `pending` → Queued for processing

### **2. Data Flow Steps**

#### **Step 1: Gmail Trigger**
```json
{
  "subject": "Amazon Order Confirmation",
  "from": "noreply@amazon.in",
  "textPlain": "Your order #123-4567890-1234567 has been confirmed. Total: ₹1,299.00",
  "messageId": "gmail_message_id_123",
  "date": "2024-01-15T10:30:00Z"
}
```

#### **Step 2: AI Transaction Detection**
```json
{
  "is_transaction": true,
  "confidence": 0.95,
  "transaction_type": "expense",
  "reasoning": "High confidence: E-commerce order confirmation with amount",
  "model_used": "openai/gpt-4"
}
```

#### **Step 3: AI Expense Extraction**
```json
{
  "amount": 1299.00,
  "currency": "INR",
  "description": "Amazon order #123-4567890-1234567",
  "category": "online_shopping",
  "merchant": "Amazon",
  "transaction_date": "2024-01-15",
  "payment_method": "upi",
  "gst_amount": 0,
  "gst_percentage": 0,
  "confidence_score": 0.92,
  "is_transaction": true
}
```

#### **Step 4: Data Parsing & Enhancement**
```json
{
  "amount": 1299.00,
  "currency": "INR",
  "description": "Amazon order #123-4567890-1234567",
  "category": "online_shopping",
  "merchant": "Amazon",
  "transaction_date": "2024-01-15",
  "payment_method": "upi",
  "gst_amount": 0,
  "gst_percentage": 0,
  "confidence_score": 0.92,
  "email_subject": "Amazon Order Confirmation",
  "email_sender": "noreply@amazon.in",
  "email_source": "gmail_message_id_123",
  "raw_email_content": "Your order #123-4567890-1234567...",
  "parsed_data": "{...complete AI response...}"
}
```

#### **Step 5: Supabase Storage**

**Insert into `expenses` table:**
```sql
INSERT INTO expenses (
    user_id, amount, currency, description, category, merchant,
    transaction_date, payment_method, gst_amount, gst_percentage,
    confidence_score, email_subject, email_sender, email_source,
    raw_email_content, parsed_data
) VALUES (
    'user-uuid', 1299.00, 'INR', 'Amazon order #123-4567890-1234567',
    'online_shopping', 'Amazon', '2024-01-15', 'upi', 0, 0,
    0.92, 'Amazon Order Confirmation', 'noreply@amazon.in',
    'gmail_message_id_123', 'Your order #123-4567890-1234567...',
    '{"amount": 1299.00, "category": "online_shopping", ...}'
);
```

**Insert into `email_processing_logs` table:**
```sql
INSERT INTO email_processing_logs (
    user_id, email_message_id, email_subject, email_sender,
    processing_status, llm_response, processing_time_ms
) VALUES (
    'user-uuid', 'gmail_message_id_123', 'Amazon Order Confirmation',
    'noreply@amazon.in', 'completed',
    '{"amount": 1299.00, "confidence": 0.92, ...}',
    1500
);
```

## 🔍 **Data Validation & Error Handling**

### **1. Required Fields**
- `user_id` → Must be valid UUID
- `amount` → Must be positive number
- `description` → Must not be empty
- `category` → Must be valid enum value
- `transaction_date` → Must be valid date

### **2. Default Values**
- `currency` → Defaults to 'INR'
- `category` → Defaults to 'other'
- `merchant` → Defaults to 'Unknown'
- `payment_method` → Defaults to 'other'
- `gst_amount` → Defaults to 0
- `confidence_score` → Defaults to 0.0

### **3. Error Handling**
- **JSON Parsing Errors** → Fallback to default values
- **Missing Fields** → Use defaults or skip record
- **Database Errors** → Log error and continue
- **AI API Errors** → Mark as failed in logs

## 📈 **Data Analytics & Queries**

### **1. Expense Summary**
```sql
SELECT 
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    AVG(amount) as average_amount
FROM expenses 
WHERE user_id = 'user-uuid'
GROUP BY category
ORDER BY total_amount DESC;
```

### **2. Processing Performance**
```sql
SELECT 
    processing_status,
    COUNT(*) as count,
    AVG(processing_time_ms) as avg_processing_time
FROM email_processing_logs 
WHERE user_id = 'user-uuid'
GROUP BY processing_status;
```

### **3. AI Confidence Analysis**
```sql
SELECT 
    category,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) as total_transactions
FROM expenses 
WHERE user_id = 'user-uuid'
GROUP BY category
HAVING AVG(confidence_score) < 0.8;
```

## 🔧 **Configuration & Customization**

### **1. User ID Mapping**
Currently uses a default UUID. For production:
- Map Gmail address to user ID
- Use Supabase auth integration
- Implement user authentication

### **2. Category Mapping**
The system supports 25+ Indian expense categories:
- `food_dining`, `transportation`, `shopping`
- `utilities`, `entertainment`, `healthcare`
- `online_shopping`, `restaurant`, `fuel`
- And many more...

### **3. Currency Conversion**
- All amounts stored in INR
- Original currency preserved in `original_currency` field
- Exchange rate stored in `exchange_rate` field

## 🚀 **Performance Optimizations**

### **1. Database Indexes**
```sql
-- Performance indexes for common queries
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_transaction_date ON expenses(transaction_date);
CREATE INDEX idx_expenses_merchant ON expenses(merchant);
CREATE INDEX idx_expenses_amount ON expenses(amount);
```

### **2. Data Retention**
- Keep raw email content for 30 days
- Archive old processing logs
- Compress parsed_data for large responses

### **3. Batch Processing**
- Process multiple emails in batches
- Use Supabase batch inserts
- Implement retry logic for failed operations

## 📊 **Monitoring & Alerts**

### **1. Key Metrics**
- **Processing Success Rate** → Should be > 95%
- **Average Processing Time** → Should be < 5 seconds
- **AI Confidence Score** → Should be > 0.8
- **Database Insert Success** → Should be 100%

### **2. Error Monitoring**
- Failed AI API calls
- Database constraint violations
- Missing required fields
- Invalid data formats

### **3. Performance Monitoring**
- Email processing queue length
- Database query performance
- AI API response times
- Storage usage trends

This data flow ensures that all transaction emails are properly processed, validated, and stored in the Supabase database with comprehensive logging for monitoring and analytics.
