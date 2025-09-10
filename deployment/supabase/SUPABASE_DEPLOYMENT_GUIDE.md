# Aeonforge Supabase Deployment Guide

## 🎯 Overview

Complete guide for deploying Aeonforge to Supabase with dynamic database schema management for 6000+ tools, user management, and real-time features.

## 📋 Pre-Deployment Setup

### 1. Install Supabase CLI
```bash
# Install Supabase CLI
npm install -g supabase

# Verify installation
supabase --version
```

### 2. Create Supabase Project
```bash
# Login to Supabase
supabase login

# Create new project (or use existing)
# Go to https://app.supabase.com/
# Click "New Project"
# Note your project URL and API keys
```

## 🗄️ Dynamic Database Schema System

### Core Schema Design for 6000+ Tools

```sql
-- Create database schema file
-- File: deployment/supabase/schema.sql

-- ========================================
-- CORE SYSTEM TABLES
-- ========================================

-- Users and Authentication (handled by Supabase Auth)
-- Additional user profile data
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    api_usage_quota INTEGER DEFAULT 1000,
    api_usage_current INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tool Categories (Dynamic)
CREATE TABLE IF NOT EXISTS tool_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    batch_number INTEGER,
    icon TEXT,
    color TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tools Registry (Dynamic for 6000+ tools)
CREATE TABLE IF NOT EXISTS tools_registry (
    id SERIAL PRIMARY KEY,
    tool_id TEXT NOT NULL UNIQUE, -- e.g., 'excel_master', 'logo_designer'
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES tool_categories(id),
    batch_number INTEGER,
    tool_number INTEGER, -- Position within batch (1-20)
    version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'maintenance')),
    complexity_level TEXT DEFAULT 'medium' CHECK (complexity_level IN ('low', 'medium', 'high')),
    execution_mode TEXT DEFAULT 'async' CHECK (execution_mode IN ('sync', 'async', 'streaming')),
    
    -- Tool Configuration (JSON)
    input_schema JSONB, -- Tool input parameters schema
    output_schema JSONB, -- Tool output format schema
    settings JSONB, -- Tool-specific settings
    metadata JSONB, -- Additional metadata
    
    -- Performance tracking
    avg_execution_time FLOAT DEFAULT 0,
    success_rate FLOAT DEFAULT 100,
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT unique_batch_tool UNIQUE (batch_number, tool_number)
);

-- Tool Executions (Usage tracking)
CREATE TABLE IF NOT EXISTS tool_executions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    tool_id TEXT REFERENCES tools_registry(tool_id),
    
    -- Execution details
    execution_id TEXT UNIQUE, -- UUID for tracking
    input_data JSONB,
    output_data JSONB,
    execution_time FLOAT, -- milliseconds
    status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout')),
    error_message TEXT,
    
    -- AI Model used
    ai_model TEXT, -- 'chatgpt', 'gemini', 'ollama'
    model_version TEXT,
    
    -- Performance metrics
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Tool Favorites
CREATE TABLE IF NOT EXISTS user_tool_favorites (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    tool_id TEXT REFERENCES tools_registry(tool_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_tool_favorite UNIQUE (user_id, tool_id)
);

-- System Health Monitoring
CREATE TABLE IF NOT EXISTS system_health_logs (
    id BIGSERIAL PRIMARY KEY,
    inspection_id TEXT UNIQUE,
    overall_score FLOAT,
    system_status TEXT CHECK (system_status IN ('HEALTHY', 'WARNING', 'CRITICAL', 'OFFLINE')),
    total_checks INTEGER,
    passed_checks INTEGER,
    failed_checks INTEGER,
    warning_checks INTEGER,
    critical_failures INTEGER,
    
    -- Detailed results (JSON)
    inspection_results JSONB,
    performance_metrics JSONB,
    recommendations JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Model Configuration
CREATE TABLE IF NOT EXISTS ai_models (
    id SERIAL PRIMARY KEY,
    model_id TEXT NOT NULL UNIQUE, -- 'chatgpt-4', 'gemini-pro', 'ollama-llama3'
    provider TEXT NOT NULL, -- 'openai', 'google', 'ollama'
    model_name TEXT NOT NULL,
    version TEXT,
    
    -- Configuration
    is_active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 1, -- For routing decisions
    cost_per_token DECIMAL(10,8),
    max_tokens INTEGER,
    
    -- Capabilities
    supports_streaming BOOLEAN DEFAULT false,
    supports_function_calling BOOLEAN DEFAULT false,
    supports_vision BOOLEAN DEFAULT false,
    
    -- Performance tracking
    avg_response_time FLOAT,
    success_rate FLOAT DEFAULT 100,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- DYNAMIC SCHEMA MANAGEMENT
-- ========================================

-- Schema Migrations (for dynamic updates)
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    migration_id TEXT NOT NULL UNIQUE,
    migration_name TEXT NOT NULL,
    sql_up TEXT NOT NULL, -- SQL to apply migration
    sql_down TEXT, -- SQL to rollback migration
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rollback_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'rolled_back', 'failed'))
);

-- Dynamic Tool Schema Changes
CREATE TABLE IF NOT EXISTS tool_schema_updates (
    id SERIAL PRIMARY KEY,
    tool_id TEXT REFERENCES tools_registry(tool_id),
    update_type TEXT CHECK (update_type IN ('schema_change', 'new_field', 'deprecated_field', 'config_update')),
    old_schema JSONB,
    new_schema JSONB,
    migration_sql TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by UUID REFERENCES auth.users(id)
);

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Tool registry indexes
CREATE INDEX IF NOT EXISTS idx_tools_category ON tools_registry(category_id);
CREATE INDEX IF NOT EXISTS idx_tools_status ON tools_registry(status);
CREATE INDEX IF NOT EXISTS idx_tools_batch ON tools_registry(batch_number);

-- Tool executions indexes  
CREATE INDEX IF NOT EXISTS idx_executions_user ON tool_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_tool ON tool_executions(tool_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON tool_executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created ON tool_executions(created_at);

-- Health logs indexes
CREATE INDEX IF NOT EXISTS idx_health_status ON system_health_logs(system_status);
CREATE INDEX IF NOT EXISTS idx_health_created ON system_health_logs(created_at);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_tool_favorites ENABLE ROW LEVEL SECURITY;

-- User profiles - users can only see/edit their own
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);

-- Tool executions - users can only see their own executions
CREATE POLICY "Users can view own executions" ON tool_executions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own executions" ON tool_executions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User favorites - users can only manage their own favorites
CREATE POLICY "Users can view own favorites" ON user_tool_favorites FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own favorites" ON user_tool_favorites FOR ALL USING (auth.uid() = user_id);

-- Public read access for tool registry and categories
CREATE POLICY "Anyone can view tool categories" ON tool_categories FOR SELECT USING (true);
CREATE POLICY "Anyone can view active tools" ON tools_registry FOR SELECT USING (status = 'active');

-- ========================================
-- FUNCTIONS FOR DYNAMIC MANAGEMENT
-- ========================================

-- Function to add new tool category
CREATE OR REPLACE FUNCTION add_tool_category(
    category_name TEXT,
    category_description TEXT DEFAULT '',
    batch_num INTEGER DEFAULT NULL,
    icon_name TEXT DEFAULT 'tool',
    color_code TEXT DEFAULT '#3B82F6'
) RETURNS INTEGER AS $$
DECLARE
    new_category_id INTEGER;
BEGIN
    INSERT INTO tool_categories (name, description, batch_number, icon, color)
    VALUES (category_name, category_description, batch_num, icon_name, color_code)
    RETURNING id INTO new_category_id;
    
    RETURN new_category_id;
END;
$$ LANGUAGE plpgsql;

-- Function to register new tool
CREATE OR REPLACE FUNCTION register_tool(
    tool_identifier TEXT,
    tool_name TEXT,
    tool_description TEXT,
    category_name TEXT,
    batch_num INTEGER,
    tool_num INTEGER,
    input_schema_json JSONB DEFAULT '{}',
    output_schema_json JSONB DEFAULT '{}',
    settings_json JSONB DEFAULT '{}'
) RETURNS TEXT AS $$
DECLARE
    category_id_var INTEGER;
BEGIN
    -- Get or create category
    SELECT id INTO category_id_var FROM tool_categories WHERE name = category_name;
    
    IF category_id_var IS NULL THEN
        SELECT add_tool_category(category_name, '', batch_num) INTO category_id_var;
    END IF;
    
    -- Insert tool
    INSERT INTO tools_registry (
        tool_id, name, description, category_id, batch_number, tool_number,
        input_schema, output_schema, settings
    ) VALUES (
        tool_identifier, tool_name, tool_description, category_id_var, batch_num, tool_num,
        input_schema_json, output_schema_json, settings_json
    ) ON CONFLICT (tool_id) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        category_id = EXCLUDED.category_id,
        batch_number = EXCLUDED.batch_number,
        tool_number = EXCLUDED.tool_number,
        input_schema = EXCLUDED.input_schema,
        output_schema = EXCLUDED.output_schema,
        settings = EXCLUDED.settings,
        updated_at = NOW();
    
    RETURN tool_identifier;
END;
$$ LANGUAGE plpgsql;

-- Function to update tool performance metrics
CREATE OR REPLACE FUNCTION update_tool_performance(
    tool_identifier TEXT,
    execution_time_ms FLOAT,
    was_successful BOOLEAN
) RETURNS VOID AS $$
BEGIN
    UPDATE tools_registry SET
        usage_count = usage_count + 1,
        avg_execution_time = (avg_execution_time * (usage_count - 1) + execution_time_ms) / usage_count,
        success_rate = CASE 
            WHEN usage_count = 1 THEN CASE WHEN was_successful THEN 100 ELSE 0 END
            ELSE (success_rate * (usage_count - 1) + CASE WHEN was_successful THEN 100 ELSE 0 END) / usage_count
        END,
        updated_at = NOW()
    WHERE tool_id = tool_identifier;
END;
$$ LANGUAGE plpgsql;

-- Function to log tool execution
CREATE OR REPLACE FUNCTION log_tool_execution(
    execution_uuid TEXT,
    user_uuid UUID,
    tool_identifier TEXT,
    input_data_json JSONB,
    ai_model_used TEXT DEFAULT 'chatgpt',
    model_version_used TEXT DEFAULT 'gpt-4'
) RETURNS BIGINT AS $$
DECLARE
    execution_log_id BIGINT;
BEGIN
    INSERT INTO tool_executions (
        execution_id, user_id, tool_id, input_data, ai_model, model_version, status
    ) VALUES (
        execution_uuid, user_uuid, tool_identifier, input_data_json, ai_model_used, model_version_used, 'pending'
    ) RETURNING id INTO execution_log_id;
    
    RETURN execution_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function to complete tool execution
CREATE OR REPLACE FUNCTION complete_tool_execution(
    execution_uuid TEXT,
    output_data_json JSONB,
    execution_time_ms FLOAT,
    execution_status TEXT DEFAULT 'completed',
    error_msg TEXT DEFAULT NULL,
    tokens_consumed INTEGER DEFAULT 0,
    execution_cost DECIMAL DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    UPDATE tool_executions SET
        output_data = output_data_json,
        execution_time = execution_time_ms,
        status = execution_status,
        error_message = error_msg,
        tokens_used = tokens_consumed,
        cost_usd = execution_cost,
        completed_at = NOW()
    WHERE execution_id = execution_uuid;
    
    -- Update tool performance metrics
    PERFORM update_tool_performance(
        (SELECT tool_id FROM tool_executions WHERE execution_id = execution_uuid),
        execution_time_ms,
        execution_status = 'completed'
    );
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- INITIAL DATA POPULATION
-- ========================================

-- Insert initial tool categories
INSERT INTO tool_categories (name, description, batch_number, icon, color) VALUES
('Code Intelligence', 'Advanced development tools for code analysis and optimization', 1, 'code', '#8B5CF6'),
('Natural Language', 'Multilingual processing and communication tools', 2, 'message-circle', '#3B82F6'),
('Business Productivity', 'Document generation and business automation', 3, 'briefcase', '#10B981'),
('Creative Design', 'Visual content creation and branding tools', 4, 'palette', '#F59E0B'),
('Data Analysis', 'Analytics, visualization and business intelligence', 5, 'bar-chart', '#EF4444')
ON CONFLICT (name) DO NOTHING;

-- Insert initial AI models
INSERT INTO ai_models (model_id, provider, model_name, version, cost_per_token, max_tokens, supports_streaming, supports_function_calling) VALUES
('chatgpt-4', 'openai', 'GPT-4', '4.0', 0.00003, 8192, true, true),
('chatgpt-3.5', 'openai', 'GPT-3.5-Turbo', '3.5', 0.000002, 4096, true, true),
('gemini-pro', 'google', 'Gemini Pro', '1.5', 0.000001, 32768, true, false),
('ollama-llama3', 'ollama', 'Llama 3', '8B', 0, 8192, false, false)
ON CONFLICT (model_id) DO NOTHING;
```

## 🚀 Supabase Deployment Commands

### Step 1: Initialize Supabase Project
```bash
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"

# Initialize Supabase in your project
supabase init

# Link to your Supabase project
supabase link --project-ref YOUR_PROJECT_REF

# Apply database schema
supabase db push

# Or apply specific migration
psql -h YOUR_PROJECT_HOST -U postgres -d postgres -f deployment/supabase/schema.sql
```

### Step 2: Set up Environment Variables
```bash
# Create production environment file
cat > .env.production << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database Connection (for direct access)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres

# API Keys (same as before)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
SERPAPI_KEY=your_serpapi_key
NIH_PUBMED_KEY=your_nih_key

# Application Settings
ENVIRONMENT=production
DEBUG=false
API_BASE_URL=https://YOUR_PROJECT_REF.supabase.co
EOF
```

### Step 3: Create Dynamic Tool Registration System
```python
# File: deployment/supabase/tool_registration.py

import os
import json
from supabase import create_client, Client
from typing import Dict, List, Any, Optional

class DynamicToolRegistration:
    """Dynamic tool registration system for Supabase"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key)
    
    def register_tool_batch(self, batch_data: Dict[str, Any]) -> bool:
        """Register an entire batch of tools"""
        try:
            batch_number = batch_data.get('batch_number')
            category_name = batch_data.get('category_name')
            tools = batch_data.get('tools', [])
            
            print(f"Registering batch {batch_number}: {category_name}")
            
            # Register each tool in the batch
            for tool_number, tool_info in enumerate(tools, 1):
                tool_id = tool_info.get('tool_id')
                
                # Call the register_tool function
                result = self.supabase.rpc('register_tool', {
                    'tool_identifier': tool_id,
                    'tool_name': tool_info.get('name'),
                    'tool_description': tool_info.get('description'),
                    'category_name': category_name,
                    'batch_num': batch_number,
                    'tool_num': tool_number,
                    'input_schema_json': tool_info.get('input_schema', {}),
                    'output_schema_json': tool_info.get('output_schema', {}),
                    'settings_json': tool_info.get('settings', {})
                }).execute()
                
                print(f"  ✅ Registered tool {tool_number}: {tool_info.get('name')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error registering batch: {e}")
            return False
    
    def scan_and_register_existing_tools(self) -> bool:
        """Scan existing tool structure and register all tools"""
        try:
            tool_batches = [
                {
                    'batch_number': 1,
                    'category_name': 'Code Intelligence',
                    'tools': self._extract_tools_from_module('tools.code_intelligence')
                },
                {
                    'batch_number': 2, 
                    'category_name': 'Natural Language',
                    'tools': self._extract_tools_from_module('tools.natural_language')
                },
                {
                    'batch_number': 3,
                    'category_name': 'Business Productivity', 
                    'tools': self._extract_tools_from_module('tools.business_productivity')
                },
                {
                    'batch_number': 4,
                    'category_name': 'Creative Design',
                    'tools': self._extract_tools_from_module('tools.creative_design')
                },
                {
                    'batch_number': 5,
                    'category_name': 'Data Analysis',
                    'tools': self._extract_tools_from_module('tools.data_analysis')
                }
            ]
            
            success_count = 0
            for batch in tool_batches:
                if self.register_tool_batch(batch):
                    success_count += 1
            
            print(f"\n✅ Successfully registered {success_count}/{len(tool_batches)} batches")
            return success_count == len(tool_batches)
            
        except Exception as e:
            print(f"❌ Error scanning tools: {e}")
            return False
    
    def _extract_tools_from_module(self, module_path: str) -> List[Dict[str, Any]]:
        """Extract tool information from a module"""
        try:
            import importlib
            module = importlib.import_module(module_path)
            
            tools = []
            if hasattr(module, 'ALL_TOOLS'):
                for tool_class in module.ALL_TOOLS:
                    tool_info = {
                        'tool_id': self._class_name_to_id(tool_class.__name__),
                        'name': self._class_name_to_display(tool_class.__name__),
                        'description': getattr(tool_class, '__doc__', '') or f"Advanced {tool_class.__name__} functionality",
                        'input_schema': {},
                        'output_schema': {},
                        'settings': {}
                    }
                    tools.append(tool_info)
            
            return tools
            
        except Exception as e:
            print(f"Warning: Could not extract tools from {module_path}: {e}")
            return []
    
    def _class_name_to_id(self, class_name: str) -> str:
        """Convert class name to tool ID"""
        # Convert CamelCase to snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _class_name_to_display(self, class_name: str) -> str:
        """Convert class name to display name"""
        # Convert CamelCase to Title Case with spaces
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', class_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    
    def add_new_tool_category(self, name: str, description: str, batch_number: int) -> bool:
        """Add a new tool category dynamically"""
        try:
            result = self.supabase.rpc('add_tool_category', {
                'category_name': name,
                'category_description': description,
                'batch_num': batch_number
            }).execute()
            
            print(f"✅ Added new category: {name}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding category: {e}")
            return False
    
    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        try:
            # Get tool execution counts
            executions = self.supabase.table('tool_executions') \
                .select('tool_id, status, execution_time, ai_model') \
                .execute()
            
            # Get tool registry info
            tools = self.supabase.table('tools_registry') \
                .select('tool_id, name, usage_count, success_rate, avg_execution_time') \
                .execute()
            
            return {
                'total_executions': len(executions.data),
                'tools_registered': len(tools.data),
                'execution_data': executions.data,
                'tool_data': tools.data
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

# Usage script
if __name__ == "__main__":
    registrar = DynamicToolRegistration()
    
    print("🚀 Starting dynamic tool registration...")
    
    # Register all existing tools
    if registrar.scan_and_register_existing_tools():
        print("✅ All tools registered successfully!")
    else:
        print("❌ Some tools failed to register")
    
    # Get usage stats
    stats = registrar.get_tool_usage_stats()
    print(f"\n📊 Statistics:")
    print(f"  Tools registered: {stats.get('tools_registered', 0)}")
    print(f"  Total executions: {stats.get('total_executions', 0)}")
```

### Step 4: Create Supabase Edge Functions
```typescript
// File: supabase/functions/tool-executor/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { toolId, inputData, userId, aiModel = 'chatgpt' } = await req.json()
    
    // Create Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )
    
    // Generate execution ID
    const executionId = crypto.randomUUID()
    
    // Log execution start
    await supabaseClient.rpc('log_tool_execution', {
      execution_uuid: executionId,
      user_uuid: userId,
      tool_identifier: toolId,
      input_data_json: inputData,
      ai_model_used: aiModel
    })
    
    // Execute tool logic here
    // This would integrate with your actual tool execution system
    const startTime = Date.now()
    
    // Simulate tool execution (replace with actual tool execution)
    const result = await executeToolLogic(toolId, inputData, aiModel)
    
    const executionTime = Date.now() - startTime
    
    // Complete execution log
    await supabaseClient.rpc('complete_tool_execution', {
      execution_uuid: executionId,
      output_data_json: result,
      execution_time_ms: executionTime,
      execution_status: 'completed',
      tokens_consumed: result.tokensUsed || 0,
      execution_cost: result.cost || 0
    })
    
    return new Response(
      JSON.stringify({ 
        success: true, 
        executionId, 
        result,
        executionTime 
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
    
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})

async function executeToolLogic(toolId: string, inputData: any, aiModel: string) {
  // This function would integrate with your tool execution system
  // For now, return a mock response
  return {
    success: true,
    output: `Tool ${toolId} executed successfully with ${aiModel}`,
    tokensUsed: 100,
    cost: 0.001
  }
}
```

### Step 5: Deploy Functions and Migrations
```bash
# Deploy edge functions
supabase functions deploy tool-executor

# Apply any database migrations
supabase db push

# Generate TypeScript types from your database
supabase gen types typescript --local > types/supabase.ts
```

### Step 6: Set up Real-time Subscriptions
```typescript
// File: deployment/supabase/realtime-setup.ts

// Enable real-time on specific tables
ALTER PUBLICATION supabase_realtime ADD TABLE tool_executions;
ALTER PUBLICATION supabase_realtime ADD TABLE system_health_logs;

// Usage in frontend:
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Subscribe to tool execution updates
const subscription = supabase
  .channel('tool-executions')
  .on('postgres_changes', 
    { 
      event: '*', 
      schema: 'public', 
      table: 'tool_executions',
      filter: `user_id=eq.${userId}`
    }, 
    (payload) => {
      console.log('Tool execution update:', payload)
    }
  )
  .subscribe()
```

## 📋 Deployment Checklist

### Pre-deployment:
- [ ] Supabase project created
- [ ] Database schema applied
- [ ] Environment variables configured
- [ ] Tool registration system tested

### Deployment:
- [ ] Edge functions deployed
- [ ] Real-time subscriptions enabled
- [ ] RLS policies active
- [ ] Initial data populated

### Post-deployment:
- [ ] Test tool execution
- [ ] Verify real-time updates
- [ ] Check performance metrics
- [ ] Monitor usage and costs

## 🔄 Dynamic Schema Updates

### Adding New Tool Categories:
```sql
-- When adding new tool batches (6-10, 11-15, etc.)
SELECT add_tool_category(
    'Healthcare Tools',
    'Medical and healthcare automation tools',
    6,
    'heart',
    '#DC2626'
);
```

### Updating Tool Schemas:
```sql
-- When tools need schema updates
UPDATE tools_registry 
SET 
    input_schema = '{"new_field": "string", "existing_field": "number"}',
    output_schema = '{"enhanced_output": "object"}',
    version = '2.0.0',
    updated_at = NOW()
WHERE tool_id = 'excel_master';
```

---

**Supabase Project**: `https://YOUR_PROJECT_REF.supabase.co`  
**Database**: PostgreSQL with real-time capabilities  
**Edge Functions**: Serverless tool execution  
**Storage**: File uploads and management  
**Auth**: Built-in user authentication