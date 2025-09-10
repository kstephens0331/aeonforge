# Aeonforge Project

Multi-Agent AI Development System - Currently in Phase 2 (Multi-Agent Collaboration)

## Project Structure
- `main.py` - Phase 1 Core Developer Agent
- `phase2_agents.py` - Phase 2 Multi-Agent System
- `tools/` - Agent tools and utilities
  - `file_tools.py` - File operations
  - `web_tools.py` - Web search with SerpAPI
  - `git_tools.py` - Git version control
  - `pdf_tools.py` - PDF generation and forms (Phase 2)
  - `approval_system.py` - Human-in-the-loop 1/2 approval (Phase 2)
  - `self_healing.py` - Error recovery system (Phase 2)
  - `api_key_manager.py` - API key management
- `test_phase2.py` - Phase 2 component tests
- `venv/` - Virtual environment
- `.env` - Environment variables (API keys)

## Commands

### Phase 8-10 Enterprise System
```bash
# Test Phase 8-10 complete implementation
python test_phase8_10.py

# Run enterprise platform integration
python phase8_10_integration.py

# Individual phase testing
python phase8_database.py
python phase9_payments.py
python phase10_ai_analytics.py
```

### Phase 1 & 2 (Terminal-based)
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Phase 1 (Core Developer Agent)
python main.py

# Run Phase 2 (Multi-Agent System)
python phase2_agents.py

# Test components
python test_phase2.py
python test_tools_simple.py
```

### Phase 3 (Web Application)
```bash
# Test Phase 3 system
python test_phase3.py

# Start backend server (Terminal 1)
start_backend.bat
# OR manually: cd backend && python main.py

# Start frontend (Terminal 2)  
start_frontend.bat
# OR manually: cd frontend && npm install && npm run dev

# Open browser to: http://localhost:3000
```

## Phase Status
- ✅ **Phase 1 Complete**: Core Developer Agent with web search, file ops, git tools
- ✅ **Phase 2 Complete**: Multi-Agent collaboration, PDF tools, self-healing, 1/2 approval
- ✅ **Phase 3 Complete**: React frontend, FastAPI backend, real-time chat, web UI
- 🚧 **Phase 4-7**: Intermediate Features (Project Templates, Advanced Workflows, etc.)
- ✅ **Phase 8 Complete**: Advanced Database Integration (PostgreSQL, Redis, Vector DB, SQLAlchemy async)
- ✅ **Phase 9 Complete**: Payment & Subscription System (Stripe, User Management, SaaS tiers, Usage tracking)
- ✅ **Phase 10 Complete**: Advanced AI Features & Analytics (Multi-model orchestration, Performance monitoring, Usage analytics)
- 🎉 **Enterprise Integration**: Complete unified platform with all advanced features operational

## API Keys Required
- `SERPAPI_KEY` - For web search functionality (get from serpapi.com)
- `STRIPE_SECRET_KEY` - For payment processing (get from stripe.com) - Phase 9
- `NIH_PUBMED_KEY` - For NIH/PubMed API access - Phase 10

## Development Notes
- Uses Ollama local LLM (llama3:8b)
- Human-in-the-loop approval system (1=approve, 2=reject)
- Self-healing error recovery
- Multi-agent collaboration between Project Manager and Senior Developer
- Never hardcodes any fake or simulated data. Will only use dynamic data to complete the working code. Any dependcies need to be installed and any public or secret keys need to be requested.