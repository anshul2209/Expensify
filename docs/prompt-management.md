# Prompt Management Strategy

## 🎯 **Recommended Approach: Hybrid System**

We use a **hybrid approach** that combines the best of both worlds:

### **1. Prompts Stored in Text Files** (`llm/prompts/`)
- ✅ **Easy to Edit**: Simple text files
- ✅ **Version Control**: Track changes in Git
- ✅ **Reusable**: Can be used by multiple systems
- ✅ **Maintainable**: Clear separation of concerns

### **2. Python API Service** (`api/prompt_manager.py`)
- ✅ **Dynamic Loading**: Load prompts at runtime
- ✅ **Caching**: Fast response times
- ✅ **API Endpoints**: Easy integration with n8n
- ✅ **Hot Reload**: Update prompts without restart

### **3. n8n Workflow Integration**
- ✅ **Dynamic Fetching**: Get prompts via HTTP requests
- ✅ **Clean JSON**: No large embedded prompts
- ✅ **Flexible**: Easy to switch prompts
- ✅ **Error Handling**: Graceful fallbacks

## 📁 **File Structure**

```
llm/prompts/
├── transaction_detection.txt          # AI agent for transaction detection
├── indian_expense_extraction.txt      # AI agent for expense extraction
└── (future prompts...)

api/
└── prompt_manager.py                  # FastAPI service for prompt management

n8n-workflows/
└── expense-automation.json            # Main workflow (fetches prompts dynamically)
```

## 🚀 **Setup Instructions**

### **1. Start the Prompt Manager Service**

```bash
# Make script executable (if not already)
chmod +x start_prompt_manager.sh

# Start the service
./start_prompt_manager.sh
```

The service will run on `http://localhost:8001`

### **2. Test the API**

```bash
# List all available prompts
curl http://localhost:8001/prompts

# Get transaction detection prompt
curl http://localhost:8001/prompts/transaction_detection

# Get expense extraction prompt
curl http://localhost:8001/prompts/indian_expense_extraction
```

### **3. Use in n8n**

Import the dynamic workflow: `n8n-workflows/expense-automation-dynamic.json`

The workflow will automatically fetch prompts from the API service.

## 🔄 **Workflow Comparison**

### **Current Workflow** (`expense-automation.json`)
```json
{
  "messages": [
    {
      "role": "system",
      "content": "{{ $('Get Expense Extraction Prompt').first().json.content }}"
    }
  ]
}
```

**Benefits:**
- ✅ Clean, readable JSON
- ✅ Easy prompt management
- ✅ Version controlled prompts
- ✅ No duplication
- ✅ Dynamic prompt fetching

## 🛠 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/prompts` | GET | List all available prompts |
| `/prompts/{prompt_type}` | GET | Get specific prompt |
| `/prompts/get` | POST | Get prompt with options |
| `/prompts/reload` | POST | Reload prompts from files |

## 📝 **Editing Prompts**

### **1. Edit Prompt Files**
```bash
# Edit transaction detection prompt
nano llm/prompts/transaction_detection.txt

# Edit expense extraction prompt
nano llm/prompts/indian_expense_extraction.txt
```

### **2. Reload Prompts**
```bash
# Reload without restarting service
curl -X POST http://localhost:8001/prompts/reload
```

### **3. Test Changes**
```bash
# Test the updated prompt
curl http://localhost:8001/prompts/transaction_detection
```

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Custom prompts directory
export PROMPTS_DIR="custom/prompts"

# Custom port
export PROMPT_MANAGER_PORT=8002
```

### **Service Configuration**
```python
# In api/prompt_manager.py
prompt_manager = PromptManager(
    prompts_dir=os.getenv("PROMPTS_DIR", "llm/prompts")
)
```

## 🚨 **Error Handling**

### **Prompt Not Found**
```json
{
  "status": "error",
  "message": "Failed to load prompt",
  "error": "Prompt not available"
}
```

### **Service Unavailable**
- n8n will show connection error
- Check if prompt manager is running
- Verify port 8001 is accessible

## 🔄 **Migration from Embedded Prompts**

### **1. Backup Current Workflow**
```bash
cp n8n-workflows/expense-automation.json n8n-workflows/expense-automation-backup.json
```

### **2. Start Prompt Manager**
```bash
./start_prompt_manager.sh
```

### **3. Import Dynamic Workflow**
- Import `expense-automation-dynamic.json` in n8n
- Configure credentials (Gmail, OpenRouter, Supabase)
- Test with sample emails

### **4. Verify Functionality**
- Check prompt loading in n8n logs
- Verify expense extraction works
- Monitor processing logs in Supabase

## 🎯 **Benefits of This Approach**

1. **Maintainability**: Easy to update prompts without touching n8n
2. **Version Control**: Track prompt changes separately
3. **Reusability**: Use same prompts in other systems
4. **Testing**: Unit test prompts independently
5. **Scalability**: Add new prompts easily
6. **Collaboration**: Multiple people can edit prompts
7. **Backup**: Easy to backup and restore prompts
8. **Performance**: Cached prompts for fast access

## 🔮 **Future Enhancements**

1. **Multi-language Support**: Hindi, regional languages
2. **Prompt Versioning**: Track prompt versions
3. **A/B Testing**: Test different prompt versions
4. **Analytics**: Track prompt performance
5. **Template System**: Dynamic prompt templates
6. **Validation**: Validate prompt syntax
7. **Backup/Restore**: Automated prompt backup
8. **Monitoring**: Health checks and alerts
