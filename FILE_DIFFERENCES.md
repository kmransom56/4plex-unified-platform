# 4-Plex Platform File Differences

## Requirements Files Comparison

### requirements-minimal.txt (23 lines) 
**Purpose**: Lightweight deployment for quick testing and basic functionality

**Contains**:
- ✅ Core FastAPI and web framework (FastAPI, uvicorn, pydantic)
- ✅ Basic database connectivity (SQLAlchemy, asyncpg, redis, neo4j)
- ✅ Essential HTTP clients (httpx, requests)
- ✅ Configuration and logging (python-dotenv, python-json-logger)

**Missing**:
- ❌ AI/ML libraries (CrewAI, OpenAI, Anthropic, LangChain)
- ❌ Web scraping tools (Selenium, BeautifulSoup, Scrapy, Playwright)
- ❌ Document processing (PyPDF2, python-docx, pandas, numpy)
- ❌ Advanced database features (Alembic migrations, py2neo)
- ❌ Testing and development tools
- ❌ Image processing and OCR
- ❌ Financial calculation libraries

### requirements.txt (123 lines)
**Purpose**: Complete production deployment with all features

**Contains Everything from minimal PLUS**:
- 🤖 **AI Frameworks**: CrewAI, OpenAI, Anthropic, LangChain
- 🕷️ **Web Scraping**: Selenium, BeautifulSoup, Scrapy, Playwright  
- 📄 **Document Processing**: PyPDF2, python-docx, openpyxl, pandas
- 🖼️ **Image Processing**: Pillow, pytesseract (OCR)
- 🧪 **Testing**: pytest, pytest-asyncio, pytest-cov
- 🔧 **Development**: black, isort, flake8, mypy
- 📊 **Data Science**: numpy, scipy, scikit-learn, xgboost
- 💰 **Financial**: numpy-financial for real estate calculations
- 🗃️ **Advanced DB**: Alembic migrations, py2neo graph operations

## Docker Compose Files Comparison

### docker-compose.simple.yml
**Purpose**: Quick deployment with core services only

**Services (5)**:
1. **unified-api** - Main FastAPI application
2. **postgres** - PostgreSQL database  
3. **redis** - Cache and session storage
4. **neo4j** - Graph database
5. **grafana** - Basic monitoring dashboard

**Features**:
- ✅ Modified ports to avoid conflicts (5434, 6381, 7475, 7688)
- ✅ Basic health monitoring
- ✅ Persistent data volumes
- ✅ Single network configuration
- ✅ Minimal resource usage

### docker-compose.yml  
**Purpose**: Complete production deployment with all microservices

**Services (10)**:
1. **unified-api** - Main FastAPI application
2. **discovery-engine** - Property discovery service (from 4plex-foreclosure-research)
3. **valuation-engine** - Property valuation service (from 4plex-investment-platform)
4. **unified-dashboard** - React frontend dashboard
5. **postgres** - PostgreSQL database
6. **redis** - Cache and session storage  
7. **neo4j** - Graph database
8. **prometheus** - Metrics collection
9. **grafana** - Advanced monitoring dashboards
10. **nginx** - Reverse proxy and load balancing

**Additional Features**:
- 🏥 **Health Checks**: Comprehensive health monitoring for all services
- 🔄 **Service Dependencies**: Proper startup ordering
- 📊 **Monitoring Stack**: Prometheus + Grafana integration
- 🌐 **Nginx Proxy**: Production-ready reverse proxy
- 📁 **More Volumes**: Additional persistent storage for logs and metrics
- 🔗 **Service Integration**: Full microservices communication setup

## When to Use Which

### Use requirements-minimal.txt + docker-compose.simple.yml when:
- ✅ Quick testing and development
- ✅ Resource-constrained environments  
- ✅ Basic API functionality testing
- ✅ Initial platform validation
- ✅ CI/CD pipeline testing
- ✅ Docker image size optimization

### Use requirements.txt + docker-compose.yml when:
- 🚀 Production deployment
- 🤖 Full AI-powered property discovery
- 📊 Complete monitoring and observability  
- 🌐 Multi-service architecture
- 📈 Scalability requirements
- 🔍 Advanced web scraping and data processing
- 💰 Complete real estate analysis features

## Current Deployment Status

**Active Configuration**: 
- ✅ Using `requirements-minimal.txt` 
- ✅ Using `docker-compose.simple.yml`
- ✅ Successfully deployed and operational

**Next Steps**:
- Upgrade to full requirements.txt for AI features
- Deploy complete docker-compose.yml for production
- Integrate original discovery and valuation services

## File Sizes & Complexity

| File | Lines | Purpose | Build Time | Resource Usage |
|------|-------|---------|------------|----------------|
| requirements-minimal.txt | 23 | Basic API | ~30 seconds | Low |
| requirements.txt | 123 | Full features | ~3-5 minutes | High |
| docker-compose.simple.yml | ~100 | 5 services | Fast | 2-4 GB RAM |
| docker-compose.yml | ~200 | 10 services | Slow | 8-16 GB RAM |

The current minimal deployment allows for rapid development and testing, while the full deployment provides production-ready capabilities with complete AI-powered real estate analysis features.