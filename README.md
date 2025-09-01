# 🏘️ 4-Plex Unified Investment Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Enabled-green.svg)](https://www.crewai.com/)

> **Comprehensive AI-powered platform combining automated 4-plex property discovery with professional investment analysis across Georgia counties.**

## ✨ Unified Features

### 🔍 **Automated Discovery Engine**
- **AI Agents**: CrewAI multi-agent system for 24/7 property discovery
- **County Coverage**: Fulton, DeKalb, Clayton, Cobb, City of Atlanta
- **Data Sources**: Foreclosure listings, tax sales, code violations, court records
- **Real-time Monitoring**: First-hour opportunity capture

### 🤖 **Professional Valuation Analysis**
- **AI-Powered Analysis**: Advanced financial modeling and risk assessment
- **Document Processing**: Automated PDF/Excel analysis and data extraction
- **Investment Scoring**: 0-100 comprehensive opportunity ranking
- **Market Intelligence**: Comparable sales, rental projections, trend analysis

### 💰 **Investment Decision Support**
- **Cap Rate Calculations**: Automated return projections
- **Cash Flow Analysis**: Monthly income and expense modeling
- **Risk Assessment**: Legal compliance, renovation estimates, market volatility
- **Portfolio Management**: Track opportunities and analyses over time

### 📊 **Unified Dashboard**
- **Discovery Status**: Real-time agent monitoring and property pipeline
- **Analysis Queue**: Automated valuation processing workflow  
- **Investment Opportunities**: Scored and ranked property listings
- **Geographic Intelligence**: County-specific heat maps and trends

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- 16GB+ RAM recommended (for AI processing)
- 100GB+ disk space

### Installation
```bash
# Clone the unified platform
git clone <repository-url>
cd 4plex-unified-platform

# Copy environment template
cp .env.example .env

# Configure API keys (see .env.example for details)
nano .env

# Start the complete platform
./scripts/start-unified-platform.sh
```

### Access Points
- **📊 Unified Dashboard**: http://localhost:11070
- **🔍 Discovery API**: http://localhost:11050  
- **💰 Valuation API**: http://localhost:11060
- **📈 Monitoring**: http://localhost:11071

## 🏗️ Unified Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    🏘️ Unified 4-Plex Platform                    │
├─────────────────┬───────────────────┬───────────────────────────┤
│  🔍 Discovery   │   💰 Valuation    │    📊 Integration Layer   │
│    Engine       │     Engine        │                           │
│  (Port 11050)   │   (Port 11060)    │     (Port 11070)         │
│                 │                   │                           │
│ • CrewAI Agents │ • Financial Model │ • Unified API             │
│ • Web Scrapers  │ • Document AI     │ • Workflow Orchestration │
│ • County APIs   │ • Investment Calc │ • Cross-System Sync       │
│ • Alert System  │ • Risk Assessment │ • Real-time Updates       │
└─────────────────┴───────────────────┴───────────────────────────┘
                             │
├─────────────────────────────┼─────────────────────────────┤
│         📊 React Unified Dashboard (Port 11071)          │
│                                                           │
│ • Discovery Status    • Investment Opportunities         │
│ • Analysis Pipeline   • Geographic Heat Maps            │
│ • Alert Management    • Portfolio Tracking              │
└───────────────────────────────────────────────────────────┘
                             │
├─────────────────────────────┼─────────────────────────────┤
│              🗄️ Unified Data Layer                       │
│                                                           │
│ • PostgreSQL (Structured Data)                          │
│ • Neo4j (Property Relationships)                        │
│ • Redis (Caching & Queues)                              │
│ • File Storage (Documents & Reports)                    │
└───────────────────────────────────────────────────────────┘
```

## 🎯 Workflow Integration

### End-to-End Property Pipeline
```
1. 📡 AI Agents → Discover Properties (24/7 monitoring)
2. ✅ Validation → Filter 4-plex properties  
3. 🔍 Enrichment → Gather market data and documents
4. 🤖 AI Analysis → Professional valuation and scoring
5. 💰 Investment Ranking → Priority-based opportunity list
6. 🚨 Smart Alerts → High-value property notifications
7. 📈 Dashboard → Visual results and portfolio tracking
```

### Automated Decision Points
- **Discovery Validation**: AI verification of 4-unit properties
- **Market Enrichment**: Automatic comparable sales research
- **Financial Analysis**: Cap rate, cash flow, ROI calculations
- **Risk Assessment**: Legal compliance, renovation requirements
- **Investment Scoring**: 0-100 composite opportunity score
- **Alert Thresholds**: Configurable notification triggers

## 📊 Service Architecture

| Service | Port | Function | Technology |
|---------|------|----------|------------|
| **Discovery Engine** | 11050 | AI agents, web scraping, data collection | Python/FastAPI, CrewAI |
| **Valuation Engine** | 11060 | Financial analysis, document processing | Python/FastAPI, AI models |
| **Integration Layer** | 11070 | API gateway, workflow orchestration | Python/FastAPI |
| **Unified Dashboard** | 11071 | React frontend, real-time updates | React 18, Material-UI |
| **Monitoring Stack** | 11072 | Grafana dashboards, Prometheus metrics | Grafana, Prometheus |
| **Database Cluster** | 5432/7474/6379 | PostgreSQL, Neo4j, Redis | Multi-database architecture |

## 🔧 Configuration

### Required API Keys
```bash
# AI Services
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Real Estate Data APIs
PROPERTYRADAR_API_KEY=your_propertyradar_key
REALESTATE_API_KEY=your_realestate_api_key
ATTOM_API_KEY=your_attom_data_key

# Database Configuration
POSTGRES_PASSWORD=secure_password_here
NEO4J_PASSWORD=secure_neo4j_password
REDIS_PASSWORD=secure_redis_password
```

### Investment Filters
```bash
# Property Criteria
MAX_PURCHASE_PRICE=500000
MIN_CAP_RATE=8.0
MIN_MONTHLY_CASH_FLOW=500
PROPERTY_TYPE=4plex

# Geographic Focus
TARGET_COUNTIES=Fulton,DeKalb,Clayton,Cobb,Atlanta

# Alert Thresholds  
HIGH_PRIORITY_SCORE=85
MEDIUM_PRIORITY_SCORE=70
```

## 🎯 Counties & Coverage

### Georgia Target Markets
- **🏙️ Fulton County** - Atlanta metro, urban core properties
- **🏘️ DeKalb County** - Eastern suburbs, diverse neighborhoods  
- **🏡 Clayton County** - Southern metro, emerging markets
- **🌳 Cobb County** - Northwestern suburbs, established areas
- **🏢 Atlanta City** - Urban investment opportunities

### Data Sources per County
- **Foreclosure Records**: Sheriff sales, tax sales, pre-foreclosures
- **Code Violations**: Municipal enforcement databases
- **Tax Information**: Delinquent tax lists, assessment data
- **Market Data**: Recent sales, rental rates, neighborhood trends

## 💼 Business Intelligence

### Investment Metrics
- **Discovery Rate**: Properties identified per day/week/month
- **Conversion Rate**: Percentage of discoveries leading to analysis
- **Investment Score Distribution**: Quality of opportunities found
- **Geographic Performance**: County-by-county opportunity density
- **Time to Analysis**: Speed from discovery to valuation complete

### ROI Optimization
- **Early Detection**: 6-12 month advantage over manual research
- **Quality Filtering**: Focus only on high-potential opportunities
- **Risk Mitigation**: Automated legal compliance checking
- **Market Timing**: Trend analysis for optimal acquisition timing
- **Portfolio Diversification**: Balanced geographic distribution

## 🛠️ Development

### Local Development Setup
```bash
# Backend development
cd backend && python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # Starts development server

# Frontend development  
cd frontend && npm install
npm run dev  # Starts React dev server

# Integration testing
./scripts/test-integration.sh
```

### Testing & Quality
```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend && npm test

# Integration tests
./scripts/run-integration-tests.sh

# Performance testing
./scripts/performance-test.sh
```

## 📚 Documentation

- [**Integration Architecture**](docs/INTEGRATION_ARCHITECTURE.md)
- [**API Documentation**](docs/API_REFERENCE.md)
- [**Deployment Guide**](docs/DEPLOYMENT.md)
- [**Development Setup**](docs/DEVELOPMENT.md)
- [**User Guide**](docs/USER_GUIDE.md)

## 🔐 Security & Compliance

### Data Protection
- **Encrypted Storage**: All sensitive data encrypted at rest
- **API Security**: JWT authentication, rate limiting
- **Privacy Compliance**: GDPR/CCPA compliant data handling
- **Audit Logging**: Comprehensive activity tracking

### Legal Compliance
- **Public Records Focus**: Prioritizes publicly available data
- **Terms of Service**: Compliant web scraping practices
- **Data Retention**: Configurable retention policies
- **Privacy Protection**: Personal information safeguards

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 **Email**: support@4plex-unified.com
- 💬 **Issues**: [GitHub Issues](../../issues)
- 📚 **Documentation**: [Wiki](../../wiki)
- 🎥 **Video Tutorials**: [Platform Playlist](link-to-videos)

---

## 🎯 Platform Integration

### Chat Copilot Platform Access
- **Platform URL**: `https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/4plex-unified`
- **Discovery Dashboard**: `/4plex-unified/discovery`
- **Valuation Dashboard**: `/4plex-unified/valuation` 
- **Investment Hub**: `/4plex-unified/opportunities`
- **System Monitoring**: `/4plex-unified/monitoring`

### AI Stack Integration
- **vLLM Reasoning**: Property analysis and legal assessment
- **vLLM Coding**: Data processing and API automation
- **vLLM General**: Market research and trend analysis
- **Platform AI Gateway**: Unified AI service access

---

**🏠💰 Built with ❤️ for serious real estate investors seeking competitive advantages through AI-powered property discovery and professional-grade investment analysis.**