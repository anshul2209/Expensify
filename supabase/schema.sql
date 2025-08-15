-- Expense Management System Database Schema (India Focused)
-- Supabase SQL schema for storing and managing expenses in INR

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE expense_category AS ENUM (
    'food_dining',
    'transportation',
    'shopping',
    'travel',
    'utilities',
    'entertainment',
    'healthcare',
    'education',
    'housing',
    'insurance',
    'groceries',
    'fuel',
    'mobile_recharge',
    'online_shopping',
    'restaurant',
    'coffee_tea',
    'street_food',
    'medicine',
    'doctor_consultation',
    'school_fees',
    'books_stationery',
    'rent',
    'maintenance',
    'electricity_bill',
    'water_bill',
    'gas_bill',
    'internet_bill',
    'mobile_bill',
    'dth_bill',
    'other'
);

CREATE TYPE transaction_type AS ENUM (
    'expense',
    'income',
    'transfer'
);

CREATE TYPE payment_method AS ENUM (
    'upi',
    'credit_card',
    'debit_card',
    'net_banking',
    'cash',
    'wallet',
    'emi',
    'other'
);

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    phone TEXT,
    city TEXT,
    state TEXT,
    gst_number TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency TEXT DEFAULT 'INR',
    original_amount DECIMAL(10,2),
    original_currency TEXT,
    exchange_rate DECIMAL(10,4),
    description TEXT NOT NULL,
    category expense_category NOT NULL,
    transaction_type transaction_type DEFAULT 'expense',
    payment_method payment_method,
    merchant TEXT,
    location TEXT,
    city TEXT,
    state TEXT,
    transaction_date DATE NOT NULL,
    email_source TEXT, -- Gmail message ID
    email_subject TEXT,
    email_sender TEXT,
    raw_email_content TEXT, -- Original email content
    parsed_data JSONB, -- LLM parsed structured data
    confidence_score DECIMAL(3,2), -- LLM confidence in classification
    tags TEXT[], -- Additional tags
    notes TEXT,
    receipt_url TEXT, -- URL to receipt image/document
    gst_amount DECIMAL(10,2), -- GST amount if applicable
    gst_percentage DECIMAL(5,2), -- GST percentage
    is_verified BOOLEAN DEFAULT FALSE, -- User verified the expense
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table for custom categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#3B82F6',
    icon TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_indian_specific BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    category expense_category,
    amount DECIMAL(10,2) NOT NULL,
    period TEXT NOT NULL, -- 'monthly', 'yearly', 'weekly'
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indian merchants table for better categorization
CREATE TABLE IF NOT EXISTS indian_merchants (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    merchant_name TEXT NOT NULL,
    category expense_category,
    subcategory TEXT,
    is_online BOOLEAN DEFAULT FALSE,
    is_offline BOOLEAN DEFAULT TRUE,
    city TEXT,
    state TEXT,
    website TEXT,
    app_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email processing logs
CREATE TABLE IF NOT EXISTS email_processing_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    email_message_id TEXT NOT NULL,
    email_subject TEXT,
    email_sender TEXT,
    processing_status TEXT NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
    llm_response JSONB,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- NLP query logs
CREATE TABLE IF NOT EXISTS nlp_query_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    query_text TEXT NOT NULL,
    query_type TEXT, -- 'analytics', 'search', 'trends'
    response_data JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_transaction_date ON expenses(transaction_date);
CREATE INDEX IF NOT EXISTS idx_expenses_email_source ON expenses(email_source);
CREATE INDEX IF NOT EXISTS idx_expenses_merchant ON expenses(merchant);
CREATE INDEX IF NOT EXISTS idx_expenses_amount ON expenses(amount);
CREATE INDEX IF NOT EXISTS idx_expenses_parsed_data ON expenses USING GIN(parsed_data);
CREATE INDEX IF NOT EXISTS idx_expenses_city ON expenses(city);
CREATE INDEX IF NOT EXISTS idx_expenses_state ON expenses(state);
CREATE INDEX IF NOT EXISTS idx_expenses_payment_method ON expenses(payment_method);

CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category);

CREATE INDEX IF NOT EXISTS idx_merchants_name ON indian_merchants(merchant_name);
CREATE INDEX IF NOT EXISTS idx_merchants_category ON indian_merchants(category);
CREATE INDEX IF NOT EXISTS idx_merchants_city ON indian_merchants(city);

CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON email_processing_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_processing_logs(processing_status);

-- Create full-text search index for expenses
CREATE INDEX IF NOT EXISTS idx_expenses_search ON expenses USING GIN(
    to_tsvector('english', description || ' ' || COALESCE(merchant, '') || ' ' || COALESCE(notes, ''))
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON indian_merchants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE indian_merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE nlp_query_logs ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Expenses policies
CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own expenses" ON expenses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own expenses" ON expenses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own expenses" ON expenses
    FOR DELETE USING (auth.uid() = user_id);

-- Categories policies
CREATE POLICY "Users can view own categories" ON categories
    FOR SELECT USING (auth.uid() = user_id OR is_default = TRUE);

CREATE POLICY "Users can insert own categories" ON categories
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own categories" ON categories
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own categories" ON categories
    FOR DELETE USING (auth.uid() = user_id);

-- Budgets policies
CREATE POLICY "Users can view own budgets" ON budgets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own budgets" ON budgets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own budgets" ON budgets
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own budgets" ON budgets
    FOR DELETE USING (auth.uid() = user_id);

-- Merchants policies (read-only for all users)
CREATE POLICY "Users can view merchants" ON indian_merchants
    FOR SELECT USING (true);

-- Logs policies
CREATE POLICY "Users can view own logs" ON email_processing_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own logs" ON email_processing_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own nlp logs" ON nlp_query_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own nlp logs" ON nlp_query_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Insert default Indian categories
INSERT INTO categories (name, description, is_default, is_indian_specific, color, icon) VALUES
    ('Food & Dining', 'Restaurants, cafes, and food delivery', TRUE, FALSE, '#EF4444', '🍽️'),
    ('Transportation', 'Public transport, cabs, fuel', TRUE, FALSE, '#3B82F6', '🚗'),
    ('Shopping', 'Clothing, electronics, general shopping', TRUE, FALSE, '#8B5CF6', '🛍️'),
    ('Travel', 'Flights, hotels, vacation expenses', TRUE, FALSE, '#06B6D4', '✈️'),
    ('Utilities', 'Electricity, water, internet, phone bills', TRUE, FALSE, '#10B981', '⚡'),
    ('Entertainment', 'Movies, games, streaming services', TRUE, FALSE, '#F59E0B', '🎬'),
    ('Healthcare', 'Medical expenses, prescriptions, insurance', TRUE, FALSE, '#EC4899', '🏥'),
    ('Education', 'Books, courses, tuition fees', TRUE, FALSE, '#84CC16', '📚'),
    ('Housing', 'Rent, mortgage, home maintenance', TRUE, FALSE, '#F97316', '🏠'),
    ('Insurance', 'Health, auto, home insurance', TRUE, FALSE, '#6366F1', '🛡️'),
    ('Groceries', 'Daily groceries and household items', TRUE, TRUE, '#22C55E', '🛒'),
    ('Fuel', 'Petrol, diesel, CNG expenses', TRUE, TRUE, '#F59E0B', '⛽'),
    ('Mobile Recharge', 'Mobile prepaid and postpaid recharges', TRUE, TRUE, '#06B6D4', '📱'),
    ('Online Shopping', 'E-commerce purchases (Amazon, Flipkart, etc.)', TRUE, TRUE, '#8B5CF6', '🛒'),
    ('Restaurant', 'Dining out at restaurants', TRUE, TRUE, '#EF4444', '🍽️'),
    ('Coffee & Tea', 'Coffee shops, tea stalls', TRUE, TRUE, '#F59E0B', '☕'),
    ('Street Food', 'Street food and local snacks', TRUE, TRUE, '#22C55E', '🍢'),
    ('Medicine', 'Pharmacy and medicine purchases', TRUE, TRUE, '#EC4899', '💊'),
    ('Doctor Consultation', 'Medical consultations and appointments', TRUE, TRUE, '#EC4899', '👨‍⚕️'),
    ('School Fees', 'School and college fees', TRUE, TRUE, '#84CC16', '🎓'),
    ('Books & Stationery', 'Books, notebooks, and stationery items', TRUE, TRUE, '#84CC16', '📚'),
    ('Rent', 'House rent and accommodation', TRUE, TRUE, '#F97316', '🏠'),
    ('Maintenance', 'Home and vehicle maintenance', TRUE, TRUE, '#F97316', '🔧'),
    ('Electricity Bill', 'Electricity and power bills', TRUE, TRUE, '#10B981', '⚡'),
    ('Water Bill', 'Water supply bills', TRUE, TRUE, '#10B981', '💧'),
    ('Gas Bill', 'LPG and gas cylinder bills', TRUE, TRUE, '#10B981', '🔥'),
    ('Internet Bill', 'Broadband and internet bills', TRUE, TRUE, '#10B981', '🌐'),
    ('Mobile Bill', 'Mobile postpaid bills', TRUE, TRUE, '#06B6D4', '📱'),
    ('DTH Bill', 'Cable TV and DTH bills', TRUE, TRUE, '#10B981', '📺'),
    ('Other', 'Miscellaneous expenses', TRUE, FALSE, '#6B7280', '📦')
ON CONFLICT DO NOTHING;

-- Insert popular Indian merchants
INSERT INTO indian_merchants (merchant_name, category, subcategory, is_online, is_offline, city, state) VALUES
    -- Food & Dining
    ('Swiggy', 'food_dining', 'food_delivery', TRUE, FALSE, 'Pan India', 'All'),
    ('Zomato', 'food_dining', 'food_delivery', TRUE, FALSE, 'Pan India', 'All'),
    ('Domino''s', 'food_dining', 'restaurant', TRUE, TRUE, 'Pan India', 'All'),
    ('Pizza Hut', 'food_dining', 'restaurant', TRUE, TRUE, 'Pan India', 'All'),
    ('KFC', 'food_dining', 'restaurant', TRUE, TRUE, 'Pan India', 'All'),
    ('McDonald''s', 'food_dining', 'restaurant', TRUE, TRUE, 'Pan India', 'All'),
    ('Starbucks', 'food_dining', 'coffee_tea', TRUE, TRUE, 'Pan India', 'All'),
    ('Cafe Coffee Day', 'food_dining', 'coffee_tea', TRUE, TRUE, 'Pan India', 'All'),
    
    -- Transportation
    ('Uber', 'transportation', 'ride_sharing', TRUE, FALSE, 'Pan India', 'All'),
    ('Ola', 'transportation', 'ride_sharing', TRUE, FALSE, 'Pan India', 'All'),
    ('Rapido', 'transportation', 'ride_sharing', TRUE, FALSE, 'Pan India', 'All'),
    ('Indian Oil', 'fuel', 'petrol_pump', FALSE, TRUE, 'Pan India', 'All'),
    ('HP', 'fuel', 'petrol_pump', FALSE, TRUE, 'Pan India', 'All'),
    ('BP', 'fuel', 'petrol_pump', FALSE, TRUE, 'Pan India', 'All'),
    
    -- Online Shopping
    ('Amazon', 'online_shopping', 'ecommerce', TRUE, FALSE, 'Pan India', 'All'),
    ('Flipkart', 'online_shopping', 'ecommerce', TRUE, FALSE, 'Pan India', 'All'),
    ('Myntra', 'online_shopping', 'fashion', TRUE, FALSE, 'Pan India', 'All'),
    ('Nykaa', 'online_shopping', 'beauty', TRUE, FALSE, 'Pan India', 'All'),
    ('BigBasket', 'groceries', 'online_groceries', TRUE, FALSE, 'Pan India', 'All'),
    ('Grofers', 'groceries', 'online_groceries', TRUE, FALSE, 'Pan India', 'All'),
    ('Blinkit', 'groceries', 'quick_commerce', TRUE, FALSE, 'Pan India', 'All'),
    
    -- Utilities
    ('Airtel', 'mobile_bill', 'telecom', TRUE, TRUE, 'Pan India', 'All'),
    ('Jio', 'mobile_bill', 'telecom', TRUE, TRUE, 'Pan India', 'All'),
    ('Vodafone', 'mobile_bill', 'telecom', TRUE, TRUE, 'Pan India', 'All'),
    ('BSNL', 'mobile_bill', 'telecom', TRUE, TRUE, 'Pan India', 'All'),
    ('Tata Sky', 'dth_bill', 'dth', TRUE, TRUE, 'Pan India', 'All'),
    ('Dish TV', 'dth_bill', 'dth', TRUE, TRUE, 'Pan India', 'All'),
    
    -- Entertainment
    ('Netflix', 'entertainment', 'streaming', TRUE, FALSE, 'Pan India', 'All'),
    ('Amazon Prime', 'entertainment', 'streaming', TRUE, FALSE, 'Pan India', 'All'),
    ('Disney+ Hotstar', 'entertainment', 'streaming', TRUE, FALSE, 'Pan India', 'All'),
    ('Spotify', 'entertainment', 'music', TRUE, FALSE, 'Pan India', 'All'),
    ('Wynk Music', 'entertainment', 'music', TRUE, FALSE, 'Pan India', 'All'),
    
    -- Healthcare
    ('Apollo Pharmacy', 'medicine', 'pharmacy', TRUE, TRUE, 'Pan India', 'All'),
    ('MedPlus', 'medicine', 'pharmacy', TRUE, TRUE, 'Pan India', 'All'),
    ('1mg', 'medicine', 'online_pharmacy', TRUE, FALSE, 'Pan India', 'All'),
    ('PharmEasy', 'medicine', 'online_pharmacy', TRUE, FALSE, 'Pan India', 'All'),
    
    -- Education
    ('Amazon Kindle', 'books_stationery', 'books', TRUE, FALSE, 'Pan India', 'All'),
    ('BookMyShow', 'entertainment', 'movies', TRUE, FALSE, 'Pan India', 'All'),
    ('Coursera', 'education', 'online_courses', TRUE, FALSE, 'Pan India', 'All'),
    ('Udemy', 'education', 'online_courses', TRUE, FALSE, 'Pan India', 'All')
ON CONFLICT DO NOTHING;
