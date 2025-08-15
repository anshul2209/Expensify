"""
Prompt Manager for Expense Management System
Manages and serves AI prompts for transaction detection and expense extraction
"""

import os
import json
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt_type: str
    language: str = "en"
    version: str = "latest"

class PromptResponse(BaseModel):
    prompt_type: str
    content: str
    version: str
    language: str

class PromptManager:
    """Manages AI prompts for the expense management system"""
    
    def __init__(self, prompts_dir: str = "llm/prompts"):
        self.prompts_dir = prompts_dir
        self.prompts_cache = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompts into cache"""
        if not os.path.exists(self.prompts_dir):
            return
        
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('.txt'):
                prompt_type = filename.replace('.txt', '')
                filepath = os.path.join(self.prompts_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.prompts_cache[prompt_type] = {
                            'content': content,
                            'version': self._get_file_version(filepath)
                        }
                except Exception as e:
                    print(f"Error loading prompt {filename}: {e}")
    
    def _get_file_version(self, filepath: str) -> str:
        """Get file modification time as version"""
        try:
            mtime = os.path.getmtime(filepath)
            return str(int(mtime))
        except:
            return "unknown"
    
    def get_prompt(self, prompt_type: str, language: str = "en", version: str = "latest") -> Optional[str]:
        """
        Get prompt content by type
        
        Args:
            prompt_type: Type of prompt (transaction_detection, expense_extraction)
            language: Language code (en, hi, etc.)
            version: Prompt version
            
        Returns:
            Prompt content or None if not found
        """
        # For now, we only have English prompts
        if language != "en":
            # Could implement multi-language support here
            pass
        
        if prompt_type in self.prompts_cache:
            return self.prompts_cache[prompt_type]['content']
        
        return None
    
    def get_prompt_info(self, prompt_type: str) -> Dict:
        """Get prompt metadata"""
        if prompt_type in self.prompts_cache:
            return {
                'type': prompt_type,
                'version': self.prompts_cache[prompt_type]['version'],
                'available': True
            }
        return {
            'type': prompt_type,
            'version': 'unknown',
            'available': False
        }
    
    def list_prompts(self) -> Dict[str, Dict]:
        """List all available prompts"""
        return {
            prompt_type: self.get_prompt_info(prompt_type)
            for prompt_type in self.prompts_cache.keys()
        }
    
    def reload_prompts(self):
        """Reload prompts from files"""
        self.prompts_cache.clear()
        self._load_prompts()

# FastAPI app for serving prompts
app = FastAPI(title="Prompt Manager API", version="1.0.0")
prompt_manager = PromptManager()

@app.get("/")
async def root():
    return {"message": "Prompt Manager API", "version": "1.0.0"}

@app.get("/prompts")
async def list_prompts():
    """List all available prompts"""
    return prompt_manager.list_prompts()

@app.post("/prompts/get")
async def get_prompt(request: PromptRequest):
    """Get prompt content"""
    content = prompt_manager.get_prompt(
        request.prompt_type, 
        request.language, 
        request.version
    )
    
    if content is None:
        raise HTTPException(status_code=404, detail=f"Prompt {request.prompt_type} not found")
    
    return PromptResponse(
        prompt_type=request.prompt_type,
        content=content,
        version=request.version,
        language=request.language
    )

@app.get("/prompts/{prompt_type}")
async def get_prompt_simple(prompt_type: str):
    """Get prompt content by type (simple GET request)"""
    content = prompt_manager.get_prompt(prompt_type)
    
    if content is None:
        raise HTTPException(status_code=404, detail=f"Prompt {prompt_type} not found")
    
    return {
        "prompt_type": prompt_type,
        "content": content,
        "version": prompt_manager.get_prompt_info(prompt_type)['version']
    }

@app.get("/prompts/all")
async def get_all_prompts():
    """Get all available prompts in a single request"""
    try:
        prompts = {}
        for prompt_type in ["transaction_detection", "indian_expense_extraction", "nlp_query"]:
            content = prompt_manager.get_prompt(prompt_type)
            if content:
                prompts[prompt_type] = content
        
        if prompts:
            return prompts
        else:
            raise HTTPException(status_code=404, detail="No prompts found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prompts/reload")
async def reload_prompts():
    """Reload prompts from files"""
    prompt_manager.reload_prompts()
    return {"message": "Prompts reloaded successfully"}

# Utility functions for direct use
def get_transaction_detection_prompt() -> str:
    """Get transaction detection prompt"""
    return prompt_manager.get_prompt("transaction_detection") or ""

def get_expense_extraction_prompt() -> str:
    """Get expense extraction prompt"""
    return prompt_manager.get_prompt("indian_expense_extraction") or ""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
