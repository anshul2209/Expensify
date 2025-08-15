"""
LLM-based Expense Classification System (India Focused)
Uses OpenRouter API to parse and classify expense emails with flexible model selection
"""

import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExpenseData:
    """Structured expense data extracted from email"""
    amount: float
    currency: str = "INR"
    original_amount: float = 0.0
    original_currency: str = "INR"
    description: str = ""
    category: str = "other"
    merchant: str = ""
    location: str = ""
    city: str = ""
    state: str = ""
    transaction_date: str = ""
    payment_method: str = ""
    confidence_score: float = 0.0
    tags: List[str] = None
    notes: str = ""
    gst_amount: float = 0.0
    gst_percentage: float = 0.0
    is_transaction: bool = False

class CurrencyConverter:
    """Currency conversion utility using exchange rate API"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.exchangerate-api.com/v4/latest"):
        """
        Initialize currency converter
        
        Args:
            api_key: API key for currency conversion service (optional)
            base_url: Base URL for exchange rate API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        
        # Fallback exchange rates (updated periodically)
        self.fallback_rates = {
            "USD": 83.15,
            "EUR": 90.85,
            "GBP": 105.50,
            "JPY": 0.56,
            "AUD": 55.20,
            "CAD": 61.80,
            "CHF": 95.40,
            "CNY": 11.65,
            "SGD": 62.10,
            "AED": 22.65,
            "SAR": 22.18,
            "INR": 1.0
        }
    
    def convert_to_inr(self, amount: float, from_currency: str) -> Tuple[float, float]:
        """
        Convert amount to INR
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            
        Returns:
            Tuple[float, float]: (converted_amount_inr, exchange_rate)
        """
        if from_currency.upper() == "INR":
            return amount, 1.0
        
        try:
            # Try to get real-time exchange rate
            exchange_rate = self._get_exchange_rate(from_currency.upper())
            converted_amount = amount * exchange_rate
            return converted_amount, exchange_rate
            
        except Exception as e:
            logger.warning(f"Failed to get exchange rate for {from_currency}: {str(e)}")
            # Use fallback rate
            fallback_rate = self.fallback_rates.get(from_currency.upper(), 1.0)
            converted_amount = amount * fallback_rate
            return converted_amount, fallback_rate
    
    def _get_exchange_rate(self, from_currency: str) -> float:
        """Get real-time exchange rate from API"""
        try:
            if self.api_key:
                # Use paid API with key
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                return data["rates"]["INR"]
            else:
                # Use free API
                url = f"{self.base_url}/{from_currency}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                return data["rates"]["INR"]
                
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {str(e)}")
            raise
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return list(self.fallback_rates.keys())

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, messages: List[Dict], model: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass

class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider for multiple LLM models"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        """
        Initialize OpenRouter provider
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate_response(self, messages: List[Dict], model: str, **kwargs) -> str:
        """
        Generate response using OpenRouter API
        
        Args:
            messages: List of message dictionaries
            model: Model to use (e.g., 'openai/gpt-4', 'anthropic/claude-3-sonnet')
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            str: Generated response
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.1),
                "max_tokens": kwargs.get("max_tokens", 1500)
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise

class ExpenseClassifier:
    """LLM-based expense classification system with flexible provider support and currency conversion (India Focused)"""
    
    def __init__(self, provider: LLMProvider, default_model: str = "openai/gpt-4", currency_converter: CurrencyConverter = None):
        """
        Initialize the expense classifier
        
        Args:
            provider: LLM provider instance (OpenRouter, OpenAI, etc.)
            default_model: Default model to use
            currency_converter: Currency converter instance
        """
        self.provider = provider
        self.default_model = default_model
        self.currency_converter = currency_converter or CurrencyConverter()
        
        # Load the comprehensive Indian expense extraction prompt
        self.system_prompt = self._load_system_prompt()
        
        # Available models on OpenRouter
        self.available_models = {
            "gpt-4": "openai/gpt-4",
            "gpt-4-turbo": "openai/gpt-4-turbo-preview",
            "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
            "claude-3-opus": "anthropic/claude-3-opus",
            "claude-3-sonnet": "anthropic/claude-3-sonnet",
            "claude-3-haiku": "anthropic/claude-3-haiku",
            "llama-3-70b": "meta-llama/llama-3-70b-instruct",
            "llama-3-8b": "meta-llama/llama-3-8b-instruct",
            "gemini-pro": "google/gemini-pro",
            "mistral-large": "mistralai/mistral-large-latest",
            "mixtral": "mistralai/mixtral-8x7b-instruct"
        }
        
        # India-focused expense categories mapping
        self.categories = {
            'food_dining': ['restaurant', 'food', 'dining', 'delivery', 'lunch', 'dinner', 'breakfast'],
            'transportation': ['uber', 'ola', 'rapido', 'taxi', 'metro', 'bus', 'train', 'auto'],
            'shopping': ['clothing', 'electronics', 'shopping', 'store', 'mall'],
            'travel': ['hotel', 'flight', 'airline', 'booking', 'travel', 'vacation', 'trip'],
            'utilities': ['electricity', 'water', 'internet', 'phone', 'utility', 'bill'],
            'entertainment': ['netflix', 'spotify', 'movie', 'game', 'entertainment', 'streaming'],
            'healthcare': ['medical', 'doctor', 'pharmacy', 'health', 'dental', 'vision'],
            'education': ['book', 'course', 'tuition', 'education', 'learning', 'school'],
            'housing': ['rent', 'mortgage', 'home', 'apartment', 'housing'],
            'insurance': ['insurance', 'coverage', 'policy'],
            'groceries': ['grocery', 'vegetables', 'fruits', 'milk', 'bread', 'rice', 'dal'],
            'fuel': ['petrol', 'diesel', 'cng', 'gas', 'fuel', 'oil'],
            'mobile_recharge': ['recharge', 'prepaid', 'postpaid', 'mobile', 'phone'],
            'online_shopping': ['amazon', 'flipkart', 'myntra', 'nykaa', 'online', 'ecommerce'],
            'restaurant': ['restaurant', 'dining', 'cafe', 'food', 'meal'],
            'coffee_tea': ['coffee', 'tea', 'starbucks', 'ccd', 'cafe'],
            'street_food': ['street', 'food', 'snack', 'chaat', 'pani', 'pur'],
            'medicine': ['medicine', 'pharmacy', 'drug', 'tablet', 'syrup'],
            'doctor_consultation': ['doctor', 'consultation', 'appointment', 'clinic', 'hospital'],
            'school_fees': ['school', 'college', 'tuition', 'fees', 'education'],
            'books_stationery': ['book', 'notebook', 'pen', 'pencil', 'stationery'],
            'rent': ['rent', 'accommodation', 'house', 'flat', 'pg'],
            'maintenance': ['maintenance', 'repair', 'service', 'mechanic'],
            'electricity_bill': ['electricity', 'power', 'bill', 'eb'],
            'water_bill': ['water', 'bill', 'supply'],
            'gas_bill': ['gas', 'lpg', 'cylinder', 'bill'],
            'internet_bill': ['internet', 'broadband', 'wifi', 'bill'],
            'mobile_bill': ['mobile', 'phone', 'bill', 'postpaid'],
            'dth_bill': ['dth', 'cable', 'tv', 'bill', 'tata', 'sky'],
            'other': ['other', 'miscellaneous', 'unknown']
        }
        
        # Indian payment methods
        self.payment_methods = {
            'upi': ['upi', 'phonepe', 'gpay', 'paytm', 'bhim'],
            'credit_card': ['credit', 'card', 'visa', 'mastercard'],
            'debit_card': ['debit', 'card', 'atm'],
            'net_banking': ['net', 'banking', 'neft', 'imps', 'rtgs'],
            'cash': ['cash', 'money'],
            'wallet': ['wallet', 'paytm', 'phonepe', 'amazon', 'pay'],
            'emi': ['emi', 'installment', 'monthly'],
            'other': ['other', 'unknown']
        }
        
        # Popular Indian merchants for better categorization
        self.indian_merchants = {
            'swiggy': 'food_dining',
            'zomato': 'food_dining',
            'dominos': 'food_dining',
            'pizza hut': 'food_dining',
            'kfc': 'food_dining',
            'mcdonalds': 'food_dining',
            'starbucks': 'coffee_tea',
            'cafe coffee day': 'coffee_tea',
            'uber': 'transportation',
            'ola': 'transportation',
            'rapido': 'transportation',
            'indian oil': 'fuel',
            'hp': 'fuel',
            'bp': 'fuel',
            'amazon': 'online_shopping',
            'flipkart': 'online_shopping',
            'myntra': 'online_shopping',
            'nykaa': 'online_shopping',
            'bigbasket': 'groceries',
            'grofers': 'groceries',
            'blinkit': 'groceries',
            'airtel': 'mobile_bill',
            'jio': 'mobile_bill',
            'vodafone': 'mobile_bill',
            'bsnl': 'mobile_bill',
            'tata sky': 'dth_bill',
            'dish tv': 'dth_bill',
            'netflix': 'entertainment',
            'amazon prime': 'entertainment',
            'disney+ hotstar': 'entertainment',
            'spotify': 'entertainment',
            'apollo pharmacy': 'medicine',
            'medplus': 'medicine',
            '1mg': 'medicine',
            'pharmeasy': 'medicine',
            'bookmyshow': 'entertainment',
            'coursera': 'education',
            'udemy': 'education'
        }
    
    def _load_system_prompt(self) -> str:
        """Load the comprehensive Indian expense extraction prompt"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'indian_expense_extraction.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Could not load system prompt file, using default")
            return "You are an expert at extracting expense information from Indian emails. Return only valid JSON."
    
    def switch_model(self, model_name: str) -> str:
        """
        Switch to a different model
        
        Args:
            model_name: Model name (e.g., 'gpt-4', 'claude-3-sonnet')
            
        Returns:
            str: Full model identifier
        """
        if model_name in self.available_models:
            self.default_model = self.available_models[model_name]
            logger.info(f"Switched to model: {self.default_model}")
            return self.default_model
        else:
            logger.warning(f"Model {model_name} not found. Available models: {list(self.available_models.keys())}")
            return self.default_model
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models"""
        return self.available_models.copy()
    
    def is_transaction_email(self, email_content: str, email_subject: str, email_sender: str) -> bool:
        """
        Determine if an email is transaction-related (India focused)
        
        Args:
            email_content: Email body content
            email_subject: Email subject
            email_sender: Email sender address
            
        Returns:
            bool: True if email is transaction-related
        """
        # Keywords that indicate transaction emails (India focused)
        transaction_keywords = [
            'receipt', 'transaction', 'payment', 'purchase', 'order', 'confirmation',
            'billing', 'invoice', 'statement', 'charge', 'debit', 'credit',
            'amazon', 'flipkart', 'myntra', 'nykaa', 'swiggy', 'zomato', 'uber', 'ola',
            'netflix', 'spotify', 'airtel', 'jio', 'vodafone', 'bsnl',
            'bank', 'credit card', 'debit card', 'paypal', 'stripe', 'upi',
            'phonepe', 'gpay', 'paytm', 'bhim', 'neft', 'imps', 'rtgs',
            'statement', 'alert', 'notification', 'successful', 'completed'
        ]
        
        # Senders that typically send transaction emails (India focused)
        transaction_senders = [
            'noreply@amazon.in', 'noreply@flipkart.com', 'noreply@myntra.com',
            'receipts@uber.com', 'receipts@ola.com', 'receipts@rapido.com',
            'noreply@swiggy.in', 'noreply@zomato.com', 'info@netflix.com',
            'no-reply@spotify.com', 'payments@paypal.com', 'noreply@stripe.com',
            'noreply@airtel.com', 'noreply@jio.com', 'noreply@vodafone.com',
            'noreply@bsnl.in', 'noreply@tatasky.com', 'noreply@dishtv.com',
            'alerts@hdfcbank.com', 'alerts@icicibank.com', 'alerts@sbicard.com'
        ]
        
        # Check subject and content for transaction keywords
        content_lower = (email_content + " " + email_subject).lower()
        
        # Check for transaction keywords
        keyword_match = any(keyword in content_lower for keyword in transaction_keywords)
        
        # Check for transaction senders
        sender_match = any(sender.lower() in email_sender.lower() for sender in transaction_senders)
        
        # Check for amount patterns (India focused - ₹, Rs, INR)
        amount_pattern = r'[₹Rs]?\s*\d+\.?\d*\s*(INR|rupees?|rs|paise?)'
        amount_match = bool(re.search(amount_pattern, content_lower))
        
        return keyword_match or sender_match or amount_match
    
    def extract_expense_data(self, email_content: str, email_subject: str, email_sender: str, model: str = None) -> ExpenseData:
        """
        Extract structured expense data from email using LLM
        
        Args:
            email_content: Email body content
            email_subject: Email subject
            email_sender: Email sender address
            model: Specific model to use (optional)
            
        Returns:
            ExpenseData: Structured expense information
        """
        try:
            # Use specified model or default
            model_to_use = model or self.default_model
            
            # Create user prompt for LLM
            user_prompt = self._create_user_prompt(email_content, email_subject, email_sender)
            
            # Call LLM API with comprehensive system prompt
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            llm_response = self.provider.generate_response(
                messages=messages,
                model=model_to_use,
                temperature=0.1,
                max_tokens=1500
            )
            
            # Extract JSON from response
            json_data = self._extract_json_from_response(llm_response)
            
            if not json_data:
                logger.warning("Failed to extract JSON from LLM response")
                return ExpenseData(amount=0.0, is_transaction=False)
            
            # Convert to ExpenseData object
            expense_data = self._json_to_expense_data(json_data)
            
            # Convert currency to INR
            expense_data = self._convert_currency_to_inr(expense_data)
            
            # Enhance with Indian merchant data
            expense_data = self._enhance_with_indian_data(expense_data)
            
            # Validate and clean data
            expense_data = self._validate_expense_data(expense_data)
            
            return expense_data
            
        except Exception as e:
            logger.error(f"Error extracting expense data: {str(e)}")
            return ExpenseData(amount=0.0, is_transaction=False)
    
    def _create_user_prompt(self, email_content: str, email_subject: str, email_sender: str) -> str:
        """Create the user prompt for LLM expense extraction"""
        
        prompt = f"""
        Please extract expense information from this Indian email:

        Email Subject: {email_subject}
        Email Sender: {email_sender}
        Email Content: {email_content}

        Follow the comprehensive guidelines provided in the system prompt to extract all financial information.
        Pay special attention to:
        - Indian currency patterns (₹, Rs, INR)
        - Indian payment methods (UPI, cards, net banking)
        - GST information
        - Indian merchant names
        - Multiple transactions if present
        - Refunds vs expenses

        Return the extracted information in the specified JSON format.
        """
        
        return prompt
    
    def _enhance_with_indian_data(self, expense_data: ExpenseData) -> ExpenseData:
        """Enhance expense data with Indian-specific information"""
        
        # Check if merchant is in our Indian merchants database
        merchant_lower = expense_data.merchant.lower()
        for merchant, category in self.indian_merchants.items():
            if merchant in merchant_lower:
                expense_data.category = category
                break
        
        # Detect payment method from email content
        content_lower = expense_data.description.lower() + " " + expense_data.merchant.lower()
        for method, keywords in self.payment_methods.items():
            if any(keyword in content_lower for keyword in keywords):
                expense_data.payment_method = method
                break
        
        # Extract GST information if present
        gst_pattern = r'GST[:\s]*₹?\s*(\d+\.?\d*)'
        gst_match = re.search(gst_pattern, content_lower)
        if gst_match:
            expense_data.gst_amount = float(gst_match.group(1))
            # Calculate GST percentage (typically 5%, 12%, 18%, 28%)
            if expense_data.amount > 0:
                expense_data.gst_percentage = (expense_data.gst_amount / expense_data.amount) * 100
        
        return expense_data
    
    def _convert_currency_to_inr(self, expense_data: ExpenseData) -> ExpenseData:
        """Convert expense amount to INR if not already in INR"""
        if expense_data.currency.upper() != "INR":
            original_amount = expense_data.amount
            original_currency = expense_data.currency
            
            try:
                converted_amount, exchange_rate = self.currency_converter.convert_to_inr(
                    original_amount, original_currency
                )
                
                expense_data.original_amount = original_amount
                expense_data.original_currency = original_currency
                expense_data.amount = converted_amount
                expense_data.currency = "INR"
                
                # Add conversion info to notes
                conversion_note = f"Converted from {original_amount} {original_currency} (Rate: {exchange_rate:.4f})"
                if expense_data.notes:
                    expense_data.notes += f" | {conversion_note}"
                else:
                    expense_data.notes = conversion_note
                
                logger.info(f"Converted {original_amount} {original_currency} to {converted_amount:.2f} INR")
                
            except Exception as e:
                logger.error(f"Currency conversion failed: {str(e)}")
                # Keep original amount if conversion fails
                expense_data.original_amount = original_amount
                expense_data.original_currency = original_currency
        
        return expense_data
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            
            # If no JSON found, try to parse the entire response
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return None
    
    def _json_to_expense_data(self, json_data: Dict) -> ExpenseData:
        """Convert JSON response to ExpenseData object"""
        
        # Default values
        default_data = {
            'amount': 0.0,
            'currency': 'INR',
            'original_amount': 0.0,
            'original_currency': 'INR',
            'description': '',
            'category': 'other',
            'merchant': '',
            'location': '',
            'city': '',
            'state': '',
            'transaction_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': '',
            'confidence_score': 0.0,
            'tags': [],
            'notes': '',
            'gst_amount': 0.0,
            'gst_percentage': 0.0,
            'is_transaction': False
        }
        
        # Update with extracted data
        for key, value in json_data.items():
            if key in default_data:
                default_data[key] = value
        
        return ExpenseData(**default_data)
    
    def _validate_expense_data(self, expense_data: ExpenseData) -> ExpenseData:
        """Validate and clean expense data"""
        
        # Ensure amount is positive
        if expense_data.amount < 0:
            expense_data.amount = abs(expense_data.amount)
        
        # Validate category
        if expense_data.category not in self.categories:
            expense_data.category = 'other'
        
        # Clean description
        if expense_data.description:
            expense_data.description = expense_data.description.strip()
        
        # Clean merchant
        if expense_data.merchant:
            expense_data.merchant = expense_data.merchant.strip()
        
        # Validate confidence score
        if not 0 <= expense_data.confidence_score <= 1:
            expense_data.confidence_score = 0.5
        
        # Ensure tags is a list
        if expense_data.tags is None:
            expense_data.tags = []
        
        return expense_data
    
    def classify_expense_category(self, description: str, merchant: str) -> Tuple[str, float]:
        """
        Classify expense category based on description and merchant
        
        Args:
            description: Expense description
            merchant: Merchant name
            
        Returns:
            Tuple[str, float]: (category, confidence_score)
        """
        text = f"{description} {merchant}".lower()
        
        best_category = 'other'
        best_score = 0.0
        
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_category = category
        
        # Normalize confidence score
        confidence = min(best_score / 3.0, 1.0)  # Max 3 keyword matches = 100% confidence
        
        return best_category, confidence
    
    def get_expense_summary(self, expenses: List[ExpenseData]) -> Dict:
        """
        Generate expense summary and analytics
        
        Args:
            expenses: List of expense data
            
        Returns:
            Dict: Summary statistics
        """
        if not expenses:
            return {
                'total_amount': 0,
                'count': 0,
                'by_category': {},
                'by_month': {},
                'by_payment_method': {},
                'average_amount': 0
            }
        
        total_amount = sum(exp.amount for exp in expenses)
        count = len(expenses)
        
        # Group by category
        by_category = {}
        for exp in expenses:
            if exp.category not in by_category:
                by_category[exp.category] = {'amount': 0, 'count': 0}
            by_category[exp.category]['amount'] += exp.amount
            by_category[exp.category]['count'] += 1
        
        # Group by month
        by_month = {}
        for exp in expenses:
            if exp.transaction_date:
                month = exp.transaction_date[:7]  # YYYY-MM
                if month not in by_month:
                    by_month[month] = {'amount': 0, 'count': 0}
                by_month[month]['amount'] += exp.amount
                by_month[month]['count'] += 1
        
        # Group by payment method
        by_payment_method = {}
        for exp in expenses:
            if exp.payment_method:
                if exp.payment_method not in by_payment_method:
                    by_payment_method[exp.payment_method] = {'amount': 0, 'count': 0}
                by_payment_method[exp.payment_method]['amount'] += exp.amount
                by_payment_method[exp.payment_method]['count'] += 1
        
        return {
            'total_amount': total_amount,
            'count': count,
            'by_category': by_category,
            'by_month': by_month,
            'by_payment_method': by_payment_method,
            'average_amount': total_amount / count if count > 0 else 0
        }

# Example usage
if __name__ == "__main__":
    # Example Indian email content
    sample_email = """
    Your Swiggy order has been confirmed!
    
    Order #SW123456789
    Order Date: December 15, 2024
    
    Restaurant: Domino's Pizza
    Items:
    - Margherita Pizza: ₹299
    - Garlic Bread: ₹99
    
    Subtotal: ₹398
    GST (5%): ₹19.90
    Delivery Fee: ₹40
    
    Total: ₹457.90
    
    Payment Method: UPI (PhonePe)
    
    Thank you for ordering with Swiggy!
    """
    
    # Initialize OpenRouter provider (you'll need to set your API key)
    # openrouter_provider = OpenRouterProvider("your-openrouter-api-key")
    
    # Initialize currency converter
    # currency_converter = CurrencyConverter()
    
    # Initialize classifier with OpenRouter and currency conversion
    # classifier = ExpenseClassifier(openrouter_provider, default_model="openai/gpt-4", currency_converter=currency_converter)
    
    # Test classification
    # expense_data = classifier.extract_expense_data(
    #     sample_email, 
    #     "Swiggy Order Confirmation", 
    #     "noreply@swiggy.in"
    # )
    # print(expense_data)
    
    # Switch to different model
    # classifier.switch_model("claude-3-sonnet")
    # expense_data_claude = classifier.extract_expense_data(
    #     sample_email, 
    #     "Swiggy Order Confirmation", 
    #     "noreply@swiggy.in",
    #     model="anthropic/claude-3-sonnet"
    # )
    # print(expense_data_claude)
