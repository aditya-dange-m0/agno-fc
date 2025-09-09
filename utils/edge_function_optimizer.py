"""
Edge Function Deployment Optimizer
==================================

Utilities for optimizing FastAPI applications for edge function deployment.
Focuses on minimal dependencies, cold start optimization, and production readiness.
"""

import os
import json
from typing import Dict, List, Optional
from pathlib import Path

def analyze_dependencies(requirements_path: str = "generated/backend/requirements.txt") -> Dict:
    """
    Analyze dependencies for edge function compatibility.
    
    Args:
        requirements_path: Path to requirements.txt file
    
    Returns:
        Analysis of dependencies with recommendations
    """
    if not os.path.exists(requirements_path):
        return {"error": "Requirements file not found"}
    
    try:
        with open(requirements_path, 'r') as f:
            requirements = f.read().strip().split('\n')
        
        # Edge-friendly dependencies
        edge_friendly = [
            'fastapi', 'uvicorn', 'pydantic', 'motor', 'pymongo',
            'python-jose', 'passlib', 'python-multipart', 'python-dotenv'
        ]
        
        # Heavy dependencies to avoid
        heavy_deps = [
            'tensorflow', 'torch', 'pandas', 'numpy', 'scipy',
            'matplotlib', 'opencv', 'pillow'
        ]
        
        analysis = {
            "total_dependencies": len(requirements),
            "edge_friendly": [],
            "potentially_heavy": [],
            "recommendations": []
        }
        
        for req in requirements:
            if req.strip():
                dep_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                
                if dep_name.lower() in edge_friendly:
                    analysis["edge_friendly"].append(dep_name)
                elif dep_name.lower() in heavy_deps:
                    analysis["potentially_heavy"].append(dep_name)
        
        # Generate recommendations
        if analysis["potentially_heavy"]:
            analysis["recommendations"].append(
                f"⚠️ Heavy dependencies detected: {', '.join(analysis['potentially_heavy'])}. "
                "Consider alternatives or lazy loading for edge functions."
            )
        
        if len(analysis["edge_friendly"]) > 0:
            analysis["recommendations"].append(
                f"✅ Edge-friendly dependencies: {', '.join(analysis['edge_friendly'])}"
            )
        
        return analysis
        
    except Exception as e:
        return {"error": f"Failed to analyze dependencies: {str(e)}"}

def optimize_fastapi_for_edge(app_path: str = "generated/backend/app.py") -> str:
    """
    Generate optimizations for FastAPI app for edge deployment.
    
    Args:
        app_path: Path to the FastAPI app file
    
    Returns:
        Optimization recommendations and code snippets
    """
    optimizations = []
    
    optimizations.append("🚀 FastAPI Edge Function Optimizations:")
    optimizations.append("=" * 50)
    
    # Cold start optimization
    optimizations.append("\n1. Cold Start Optimization:")
    optimizations.append("```python")
    optimizations.append("# Add to your FastAPI app for faster cold starts")
    optimizations.append("from fastapi import FastAPI")
    optimizations.append("from contextlib import asynccontextmanager")
    optimizations.append("")
    optimizations.append("# Global connection pool")
    optimizations.append("db_client = None")
    optimizations.append("")
    optimizations.append("@asynccontextmanager")
    optimizations.append("async def lifespan(app: FastAPI):")
    optimizations.append("    # Startup")
    optimizations.append("    global db_client")
    optimizations.append("    db_client = AsyncIOMotorClient(MONGODB_URL)")
    optimizations.append("    yield")
    optimizations.append("    # Shutdown")
    optimizations.append("    if db_client:")
    optimizations.append("        db_client.close()")
    optimizations.append("")
    optimizations.append("app = FastAPI(lifespan=lifespan)")
    optimizations.append("```")
    
    # Environment configuration
    optimizations.append("\n2. Environment Configuration:")
    optimizations.append("```python")
    optimizations.append("# Optimize for edge environment")
    optimizations.append("import os")
    optimizations.append("")
    optimizations.append("# Edge function settings")
    optimizations.append("ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')")
    optimizations.append("DEBUG = ENVIRONMENT == 'development'")
    optimizations.append("")
    optimizations.append("app = FastAPI(")
    optimizations.append("    title='Edge API',")
    optimizations.append("    debug=DEBUG,")
    optimizations.append("    docs_url='/docs' if DEBUG else None,")
    optimizations.append("    redoc_url='/redoc' if DEBUG else None")
    optimizations.append(")")
    optimizations.append("```")
    
    # Minimal CORS setup
    optimizations.append("\n3. Minimal CORS Configuration:")
    optimizations.append("```python")
    optimizations.append("from fastapi.middleware.cors import CORSMiddleware")
    optimizations.append("")
    optimizations.append("# Minimal CORS for production")
    optimizations.append("app.add_middleware(")
    optimizations.append("    CORSMiddleware,")
    optimizations.append("    allow_origins=os.getenv('ALLOWED_ORIGINS', '*').split(','),")
    optimizations.append("    allow_credentials=True,")
    optimizations.append("    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],")
    optimizations.append("    allow_headers=['*']")
    optimizations.append(")")
    optimizations.append("```")
    
    # Health check
    optimizations.append("\n4. Lightweight Health Check:")
    optimizations.append("```python")
    optimizations.append("@app.get('/health')")
    optimizations.append("async def health_check():")
    optimizations.append("    return {")
    optimizations.append("        'status': 'healthy',")
    optimizations.append("        'timestamp': datetime.utcnow().isoformat(),")
    optimizations.append("        'environment': ENVIRONMENT")
    optimizations.append("    }")
    optimizations.append("```")
    
    return "\n".join(optimizations)

def generate_edge_deployment_config() -> Dict:
    """
    Generate configuration files for edge deployment.
    
    Returns:
        Dictionary with deployment configuration files
    """
    configs = {}
    
    # Vercel configuration
    configs["vercel.json"] = {
        "version": 2,
        "builds": [
            {
                "src": "app.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "app.py"
            }
        ],
        "env": {
            "MONGODB_URL": "@mongodb_url",
            "JWT_SECRET": "@jwt_secret",
            "ENVIRONMENT": "production"
        }
    }
    
    # Netlify configuration
    configs["netlify.toml"] = """[build]
  command = "pip install -r requirements.txt"
  functions = "netlify/functions"

[build.environment]
  PYTHON_VERSION = "3.9"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/app/:splat"
  status = 200
"""
    
    # Railway configuration
    configs["railway.json"] = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn app:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health"
        }
    }
    
    # Docker configuration for edge
    configs["Dockerfile"] = """FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    return configs

def create_production_checklist() -> List[str]:
    """
    Create a production readiness checklist for edge deployment.
    
    Returns:
        List of checklist items
    """
    checklist = [
        "🔒 Security Checklist:",
        "  ✅ Environment variables for sensitive data (MONGODB_URL, JWT_SECRET)",
        "  ✅ CORS configured with specific origins (not '*' in production)",
        "  ✅ Input validation with Pydantic models",
        "  ✅ Rate limiting implemented (if needed)",
        "  ✅ Authentication/authorization in place",
        "",
        "⚡ Performance Checklist:",
        "  ✅ Database connection pooling configured",
        "  ✅ Async/await used for all I/O operations",
        "  ✅ Response compression enabled",
        "  ✅ Minimal dependencies in requirements.txt",
        "  ✅ Cold start optimization implemented",
        "",
        "🔧 Deployment Checklist:",
        "  ✅ Health check endpoint (/health) implemented",
        "  ✅ Proper error handling and logging",
        "  ✅ Environment-specific configuration",
        "  ✅ Database indexes defined for queries",
        "  ✅ API documentation disabled in production",
        "",
        "📊 Monitoring Checklist:",
        "  ✅ Structured logging implemented",
        "  ✅ Error tracking configured",
        "  ✅ Performance monitoring in place",
        "  ✅ Database connection monitoring",
        "",
        "🧪 Testing Checklist:",
        "  ✅ Unit tests for business logic",
        "  ✅ Integration tests for API endpoints",
        "  ✅ Load testing for expected traffic",
        "  ✅ Edge function cold start testing"
    ]
    
    return checklist

def optimize_project_for_edge(project_path: str = "generated/backend") -> str:
    """
    Analyze and optimize entire project for edge deployment.
    
    Args:
        project_path: Path to the backend project
    
    Returns:
        Comprehensive optimization report
    """
    if not os.path.exists(project_path):
        return f"❌ Project path not found: {project_path}"
    
    report = []
    report.append("🚀 Edge Function Optimization Report")
    report.append("=" * 50)
    
    # Analyze dependencies
    deps_analysis = analyze_dependencies(f"{project_path}/requirements.txt")
    if "error" not in deps_analysis:
        report.append(f"\n📦 Dependencies Analysis:")
        report.append(f"  Total dependencies: {deps_analysis['total_dependencies']}")
        report.append(f"  Edge-friendly: {len(deps_analysis['edge_friendly'])}")
        report.append(f"  Potentially heavy: {len(deps_analysis['potentially_heavy'])}")
        
        for rec in deps_analysis.get("recommendations", []):
            report.append(f"  {rec}")
    
    # Check file structure
    report.append(f"\n📁 Project Structure:")
    files = []
    for root, dirs, filenames in os.walk(project_path):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), project_path)
            files.append(rel_path)
    
    report.append(f"  Files found: {len(files)}")
    for file in files:
        report.append(f"    📄 {file}")
    
    # Generate optimizations
    report.append(f"\n{optimize_fastapi_for_edge()}")
    
    # Production checklist
    report.append(f"\n📋 Production Readiness Checklist:")
    checklist = create_production_checklist()
    report.extend(checklist)
    
    return "\n".join(report)

if __name__ == "__main__":
    # Test the optimizer
    print(optimize_project_for_edge())