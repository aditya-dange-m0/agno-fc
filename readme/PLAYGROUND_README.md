# Enhanced Development Playground

The Enhanced Development Playground provides an interactive web interface for testing both individual agents and the complete team orchestrator with enhanced iteration capabilities.

## 🚀 Quick Start

### Option 1: Easy Start (Recommended)
```bash
python start_playground.py
```

### Option 2: Direct Start
```bash
python enhanced_playground.py
```

### Option 3: Using uvicorn
```bash
uvicorn enhanced_playground:app --host 0.0.0.0 --port 7777 --reload
```

## 🌐 Access

Once started, open your browser to:
```
http://localhost:7777
```

## 🎮 Features

### Individual Agents
Test each agent separately:
- **Planner Agent**: Create project plans and requirements analysis
- **Backend Agent**: Generate FastAPI backends with enhanced tools
- **Frontend Agent**: Create React/Next.js frontends

### Team Orchestrator
Test the complete team workflow:
- **Automatic mode detection** (first generation vs iterative refinement)
- **Team coordination** with shared state management
- **Enhanced workflows** supporting both new projects and updates
- **Memory persistence** across sessions

## 💡 Usage Examples

### Individual Agent Testing
```
# Test Backend Agent
"Create a FastAPI app for user management with MongoDB"

# Test Frontend Agent  
"Create a React dashboard with user authentication"

# Test Planner Agent
"Plan a social media application with real-time features"
```

### Team Orchestrator Testing
```
# First Generation Workflow
"Create a complete e-commerce platform with user auth and product management"

# Iterative Refinement Workflow
"Add real-time notifications to the existing e-commerce platform"

# Interactive Commands
"/analyze" - Analyze current project structure
"/workflow Build a blog platform" - Run complete workflow
"/status" - Check development status
"/backup" - Create project backup
```

## 🔧 Environment Setup

### Required Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Optional Environment Variables
```env
# Database configuration (if using MongoDB)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=your_database_name

# JWT configuration (for authentication)
JWT_SECRET=your_jwt_secret_here

# Environment setting
ENVIRONMENT=development
```

## 📁 Project Structure

```
agno-fc/
├── enhanced_playground.py      # Main playground application
├── start_playground.py         # Easy startup script
├── main.py                     # Team orchestrator
├── agents/                     # Individual agents
│   ├── planner_agent.py
│   ├── backend_agent.py
│   └── frontend_agent.py
├── utils/                      # Utilities
│   ├── artifact_parser.py
│   └── edge_function_optimizer.py
├── generated/                  # Generated code output
│   ├── backend/
│   └── frontend/
└── .env                        # Environment variables
```

## 🎯 Testing Scenarios

### Scenario 1: New Project Creation
1. Start with team orchestrator
2. Request: "Create a task management app with user authentication"
3. Watch the team coordinate through planning, backend, and frontend phases
4. Check generated files in `./generated/` directory

### Scenario 2: Iterative Enhancement
1. Ensure you have existing generated files
2. Request: "Add real-time notifications to the task management app"
3. Watch the team detect iterative mode and make targeted updates
4. Verify existing functionality is preserved

### Scenario 3: Individual Agent Testing
1. Select Backend Agent
2. Request: "Analyze the current project structure and optimize for edge deployment"
3. Test the enhanced tools and analysis capabilities

## 🔍 Debugging Features

### Memory Persistence
- All conversations are stored in SQLite database
- Session summaries are automatically created
- User preferences and facts are remembered

### Enhanced Logging
- Tool calls are visible in the interface
- Team member responses are shown
- Progress tracking across phases

### File Management
- Generated files are automatically saved
- Backups are created before modifications
- Project structure analysis is available

## 🚀 Advanced Features

### Edge Deployment Optimization
```
"Optimize the current backend for Vercel edge deployment"
```

### Project Analysis
```
"Analyze the current project structure and suggest improvements"
```

### Search Capabilities
```
"Search for all FastAPI imports in the project files"
```

### Safe File Operations
```
"Add a new user profile endpoint to the existing backend"
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Variables
```bash
# Check .env file exists and contains OPENAI_API_KEY
cat .env
```

#### 3. Port Already in Use
```bash
# Change port in enhanced_playground.py or kill existing process
lsof -ti:7777 | xargs kill -9
```

#### 4. Memory Database Issues
```bash
# Remove existing database to reset
rm dev_team_memory.db
```

### Debug Mode
Set environment variable for verbose logging:
```env
DEBUG=true
AGNO_LOG_LEVEL=DEBUG
```

## 📊 Performance Tips

### For Better Response Times
- Use specific, clear requests
- Test individual agents first before team workflows
- Keep generated projects reasonably sized

### For Memory Management
- Restart playground periodically for long sessions
- Clear generated files if disk space is limited
- Monitor memory database size

## 🎉 Success Indicators

### Playground is Working When:
- ✅ Web interface loads at http://localhost:7777
- ✅ Individual agents respond to queries
- ✅ Team orchestrator coordinates properly
- ✅ Files are generated in `./generated/` directory
- ✅ Memory persists across sessions

### Enhanced Features are Working When:
- ✅ Mode detection works (first gen vs iterative)
- ✅ Project analysis shows current structure
- ✅ Search finds content across files
- ✅ Backups are created before changes
- ✅ Edge optimization provides recommendations

## 🔗 Related Documentation

- [Enhanced Backend README](./ENHANCED_BACKEND_README.md) - Backend agent capabilities
- [Enhanced Orchestrator README](./ENHANCED_ORCHESTRATOR_README.md) - Team coordination
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Complete feature overview

## 🤝 Contributing

To add new features to the playground:
1. Modify `enhanced_playground.py` for playground configuration
2. Update agent files for new capabilities
3. Add tests in the respective test files
4. Update this README with new features

The Enhanced Development Playground provides a comprehensive testing environment for the full-stack development team with advanced iteration capabilities!