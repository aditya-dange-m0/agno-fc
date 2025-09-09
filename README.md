# AGNO Full-Stack Development Team

An enhanced AI-powered development team that creates complete full-stack applications with intelligent iteration support and edge deployment optimization.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/aditya-dange-m0/agno-fc.git
cd agno-fc

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start the Playground
```bash
# Easy start (recommended)
python start_playground.py

# Or test setup first
python test_playground_setup.py
```

### 3. Access the Interface
Open your browser to: **http://localhost:7777**

## 🎯 Features

### 🤖 **Enhanced AI Agents**
- **Planner Agent**: Creates comprehensive project plans and requirements analysis
- **Backend Agent**: Generates FastAPI backends with MongoDB, authentication, and edge optimization
- **Frontend Agent**: Creates React/Next.js frontends with modern styling and API integration

### 🔄 **Dual Generation Modes**
- **First Generation**: Complete project scaffolding from scratch
- **Iterative Refinement**: Targeted updates to existing code without breaking functionality

### 🔍 **Advanced Tools**
- **Project Search**: Find content across all generated files
- **Safe File Operations**: Automatic backups before modifications
- **Structure Analysis**: Comprehensive project overview and status
- **Edge Optimization**: Production-ready deployment configurations

### 🤝 **Team Orchestration**
- **Intelligent Coordination**: Automatic workflow detection and team coordination
- **Memory Persistence**: Conversations and project state saved across sessions
- **Progress Tracking**: Real-time status monitoring and validation

## 📋 Usage Examples

### Create New Project
```
"Create a task management app with user authentication and real-time updates"
```

### Enhance Existing Project
```
"Add payment processing to the existing e-commerce platform"
```

### Individual Agent Testing
```
# Backend Agent
"Optimize the current backend for Vercel edge deployment"

# Frontend Agent  
"Add a dark mode toggle to the existing dashboard"

# Planner Agent
"Plan the architecture for a social media platform"
```

## 🏗️ Project Structure

```
agno-fc/
├── 🎮 Playground & Setup
│   ├── enhanced_playground.py      # Main playground application
│   ├── start_playground.py         # Easy startup script
│   ├── test_playground_setup.py    # Setup verification
│   └── requirements.txt            # Dependencies
│
├── 🤖 AI Agents
│   ├── agents/
│   │   ├── planner_agent.py       # Project planning
│   │   ├── backend_agent.py       # Enhanced backend generation
│   │   └── frontend_agent.py      # Frontend development
│   └── main.py                    # Team orchestrator
│
├── 🛠️ Utilities
│   └── utils/
│       ├── artifact_parser.py     # Code extraction
│       └── edge_function_optimizer.py  # Edge deployment
│
├── 📁 Generated Code
│   └── generated/
│       ├── backend/               # FastAPI applications
│       └── frontend/              # React/Next.js apps
│
├── 🧪 Testing
│   ├── test_enhanced_backend.py   # Backend agent tests
│   └── test_enhanced_orchestrator.py  # Team tests
│
└── 📚 Documentation
    ├── PLAYGROUND_README.md       # Playground guide
    ├── ENHANCED_BACKEND_README.md # Backend capabilities
    ├── ENHANCED_ORCHESTRATOR_README.md  # Team coordination
    └── IMPLEMENTATION_SUMMARY.md  # Complete feature overview
```

## 🎮 Interactive Commands

### Playground Commands
```bash
/analyze                    # Analyze current project
/plan <requirements>        # Create/update project plan
/backend                   # Generate/update backend
/frontend                  # Generate/update frontend
/status                    # Check development status
/backup                    # Create project backup
/workflow <requirements>   # Run complete workflow
/optimize                  # Optimize for edge deployment
/search <query>           # Search project files
```

### Team Workflows
```bash
# First Generation
python main.py "Create a blog platform with user auth"

# Interactive Mode
python main.py
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=your_database_name
JWT_SECRET=your_jwt_secret_here
ENVIRONMENT=development
```

### Playground Settings
- **Host**: 0.0.0.0 (accessible from network)
- **Port**: 7777 (configurable in enhanced_playground.py)
- **Auto-reload**: Enabled for development

## 🚀 Production Features

### Edge Deployment Ready
- **Cold Start Optimization**: Efficient connection pooling and startup
- **Minimal Dependencies**: Lightweight, edge-friendly packages
- **Production Configs**: Ready-to-use configurations for:
  - Vercel Edge Functions
  - Netlify Functions
  - Railway Deployment
  - Docker Containers

### Security & Best Practices
- **JWT Authentication**: Secure user management
- **Input Validation**: Pydantic models with proper validation
- **CORS Configuration**: Production-ready cross-origin settings
- **Environment Variables**: Secure configuration management

### Database & Performance
- **MongoDB with Motor**: Async database operations
- **Connection Pooling**: Efficient resource management
- **Aggregation Pipelines**: Optimized complex queries
- **Index Suggestions**: Performance optimization recommendations

## 🧪 Testing

### Setup Verification
```bash
python test_playground_setup.py
```

### Component Testing
```bash
# Test backend agent
python test_enhanced_backend.py

# Test team orchestrator
python test_enhanced_orchestrator.py
```

### Manual Testing
1. Start playground: `python start_playground.py`
2. Open browser: http://localhost:7777
3. Test individual agents and team workflows
4. Verify generated files in `./generated/` directory

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Key Missing**: Check `.env` file has `OPENAI_API_KEY`
3. **Port In Use**: Change port in `enhanced_playground.py` or kill process
4. **Memory Issues**: Remove `dev_team_memory.db` to reset

### Debug Mode
```env
DEBUG=true
AGNO_LOG_LEVEL=DEBUG
```

## 📊 Performance Tips

- Use specific, clear requests for better results
- Test individual agents before complex team workflows
- Monitor generated file sizes and clean up periodically
- Restart playground for long development sessions

## 🎉 Success Indicators

✅ **Setup Complete When**:
- Playground loads at http://localhost:7777
- Individual agents respond to queries
- Team orchestrator coordinates properly
- Files generate in `./generated/` directory

✅ **Enhanced Features Working When**:
- Mode detection works (first gen vs iterative)
- Project analysis shows structure
- Search finds content across files
- Backups create before changes
- Edge optimization provides recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Update documentation as needed
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Playground Guide](./PLAYGROUND_README.md) - Detailed playground usage
- [Backend Agent](./ENHANCED_BACKEND_README.md) - Backend capabilities
- [Team Orchestrator](./ENHANCED_ORCHESTRATOR_README.md) - Team coordination
- [Implementation Details](./IMPLEMENTATION_SUMMARY.md) - Complete feature overview

---

**Ready to build amazing full-stack applications with AI? Start the playground and let the team create your next project!** 🚀