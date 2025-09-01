# 🔄 Migration Guide: From Separate Apps to Unified Platform

## 📋 **Migration Overview**

This guide helps you transition from the two separate applications to the new unified 4-Plex Investment Platform.

### **Before Migration** (Current State)
- **4-Plex Foreclosure Research**: `/home/keith/chat-copilot/4plex-foreclosure-research/`
- **4-Plex Investment Platform**: `/home/keith/chat-copilot/4plex-investment-platform/`

### **After Migration** (Target State)
- **4-Plex Unified Platform**: `/home/keith/chat-copilot/4plex-unified-platform/`

## 🗂️ **Data Migration**

### **Step 1: Backup Existing Data**
```bash
# Create backup directory
mkdir -p /home/keith/backups/4plex-migration-$(date +%Y%m%d)
cd /home/keith/backups/4plex-migration-$(date +%Y%m%d)

# Backup foreclosure research data
cp -r /home/keith/chat-copilot/4plex-foreclosure-research/data ./foreclosure-data
cp /home/keith/chat-copilot/4plex-foreclosure-research/.env ./foreclosure-env

# Backup investment platform data
cp -r /home/keith/chat-copilot/4plex-investment-platform/data ./investment-data
cp /home/keith/chat-copilot/4plex-investment-platform/.env ./investment-env
```

### **Step 2: Database Migration**
The unified platform uses shared databases. If you have existing data:

```bash
# Export existing PostgreSQL data (if any)
pg_dump -h localhost -U postgres foreclosure_research > foreclosure_dump.sql
pg_dump -h localhost -U postgres investment_platform > investment_dump.sql

# Export Neo4j data (if any)
docker exec neo4j-container cypher-shell -u neo4j -p password \
  "MATCH (n) RETURN n" > neo4j_export.cypher
```

## ⚙️ **Environment Configuration Migration**

### **Step 3: Merge Environment Variables**
Create the unified `.env` file by combining settings from both applications:

```bash
cd /home/keith/chat-copilot/4plex-unified-platform

# Start with the template
cp .env.example .env

# Edit with your merged configuration
nano .env
```

**Key Variables to Migrate:**
```bash
# From both applications
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# From foreclosure research
PROPERTYRADAR_API_KEY=your_propertyradar_key
REALESTATE_API_KEY=your_realestate_key
ATTOM_API_KEY=your_attom_key

# Database passwords (use new secure passwords)
POSTGRES_PASSWORD=new_secure_password
NEO4J_PASSWORD=new_secure_password
REDIS_PASSWORD=new_secure_password

# Investment criteria from both apps
MAX_PURCHASE_PRICE=500000
MIN_CAP_RATE=8.0
TARGET_COUNTIES=Fulton,DeKalb,Clayton,Cobb,Atlanta
```

## 🚀 **Service Migration**

### **Step 4: Stop Existing Services**
```bash
# Stop foreclosure research services
cd /home/keith/chat-copilot/4plex-foreclosure-research
./scripts/stop-system.sh  # or docker-compose down

# Stop investment platform services
cd /home/keith/chat-copilot/4plex-investment-platform
docker-compose down  # or your stop method
```

### **Step 5: Deploy Unified Platform**
```bash
cd /home/keith/chat-copilot/4plex-unified-platform

# Deploy the unified platform
./scripts/start-unified-platform.sh
```

### **Step 6: Verify Migration**
```bash
# Check all services are running
docker-compose ps

# Verify health endpoints
curl http://localhost:11070/health  # Unified API
curl http://localhost:11050/health  # Discovery Engine  
curl http://localhost:11060/health  # Valuation Engine

# Access dashboards
echo "Main Dashboard: http://localhost:11071"
echo "Monitoring: http://localhost:11072"
```

## 📊 **Data Import Process**

### **Step 7: Import Historical Data (Optional)**
If you have existing property data to import:

```bash
# Import to unified database
python -c "
import asyncio
from backend.integration.data_importer import DataImporter

async def main():
    importer = DataImporter()
    
    # Import foreclosure research data
    await importer.import_foreclosure_data('/path/to/foreclosure-data')
    
    # Import investment platform data
    await importer.import_investment_data('/path/to/investment-data')

asyncio.run(main())
"
```

## 🔗 **Platform Integration Update**

### **Step 8: Update Chat Copilot Platform nginx**
Update the nginx configuration to point to the unified platform:

```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/ai-hub.conf

# Replace old endpoints with:
location /4plex-unified/ {
    proxy_pass http://127.0.0.1:11070/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx
```

### **Step 9: Update Platform Access**
The unified platform will be accessible at:
- **Platform URL**: `https://ubuntuaicodeserver-1.tail5137b4.ts.net:10443/4plex-unified`

## 🧪 **Testing Migration**

### **Step 10: End-to-End Testing**
```bash
# Test discovery functionality
curl -X POST http://localhost:11070/api/discovery/start \
  -H "Content-Type: application/json" \
  -d '{
    "counties": ["Fulton"],
    "property_types": ["4plex"],
    "max_price": 500000
  }'

# Test valuation functionality  
curl -X POST http://localhost:11070/api/valuation/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "test-property-id",
    "priority": "normal"
  }'

# Test unified workflow
curl http://localhost:11070/api/properties
curl http://localhost:11070/api/opportunities
```

## 📱 **Frontend Migration**

### **Step 11: Dashboard Access**
The unified dashboard combines functionality from both applications:

**Old Access:**
- Foreclosure Research: `http://localhost:11051`
- Investment Platform: `http://localhost:11061`

**New Unified Access:**
- **Main Dashboard**: `http://localhost:11071`
- **API Documentation**: `http://localhost:11070/api/docs`
- **System Monitoring**: `http://localhost:11072`

## 🛠️ **Troubleshooting Migration**

### **Common Issues and Solutions**

**Issue**: Services not starting
```bash
# Check logs
docker-compose logs unified-api
docker-compose logs discovery-engine
docker-compose logs valuation-engine

# Verify environment variables
grep -v '^#' .env | grep -v '^$'
```

**Issue**: Database connection errors
```bash
# Verify database services
docker-compose ps postgres redis neo4j

# Test connections
docker-compose exec postgres psql -U postgres -d unified_properties -c "SELECT 1"
docker-compose exec redis redis-cli ping
```

**Issue**: Port conflicts
```bash
# Check what's using the ports
sudo netstat -tlnp | grep -E ":(11070|11071|11072|5432|6379|7474)"

# Stop conflicting services
sudo systemctl stop <service-name>
# or
docker stop <container-name>
```

## 📦 **Post-Migration Cleanup**

### **Step 12: Clean Up Old Applications**
⚠️ **Only after verifying unified platform works correctly**

```bash
# Archive old applications (don't delete yet)
mkdir -p /home/keith/archived-apps/$(date +%Y%m%d)
mv /home/keith/chat-copilot/4plex-foreclosure-research /home/keith/archived-apps/$(date +%Y%m%d)/
mv /home/keith/chat-copilot/4plex-investment-platform /home/keith/archived-apps/$(date +%Y%m%d)/

# Clean up old Docker containers and images
docker system prune -f
```

## ✅ **Migration Verification Checklist**

### **Functional Testing**
- [ ] Unified API responds to health checks
- [ ] Discovery engine can start county searches
- [ ] Valuation engine can analyze properties
- [ ] Dashboard loads and displays data
- [ ] Monitoring system shows metrics
- [ ] Database connections working
- [ ] All service logs show healthy status

### **Integration Testing**
- [ ] End-to-end workflow: Discovery → Valuation → Scoring
- [ ] Cross-system data synchronization working
- [ ] Alert system generating notifications
- [ ] Platform nginx integration working
- [ ] All API endpoints responding correctly

### **Performance Testing**
- [ ] Response times under 2 seconds for API calls
- [ ] Discovery agents can handle multiple counties
- [ ] Valuation engine processes properties within 15 minutes
- [ ] Dashboard loads within 3 seconds
- [ ] System handles 100+ concurrent requests

## 🎯 **Migration Success Criteria**

✅ **Migration is successful when:**
1. All unified platform services are running and healthy
2. Discovery and valuation functionality works end-to-end
3. Historical data (if any) has been imported successfully
4. Platform integration is working through nginx
5. Performance meets or exceeds original applications
6. All team members can access and use the new interface

## 📞 **Migration Support**

### **If You Need Help**
- **Check Logs**: `docker-compose logs -f [service-name]`
- **System Status**: `./scripts/start-unified-platform.sh status`
- **Health Checks**: Visit `http://localhost:11070/health`
- **Documentation**: Review `/docs` directory for detailed guides

### **Rollback Plan** (Emergency)
If the migration fails and you need to restore the original applications:

```bash
# Stop unified platform
cd /home/keith/chat-copilot/4plex-unified-platform
docker-compose down

# Restore from archive
cd /home/keith/chat-copilot
mv /home/keith/archived-apps/$(date +%Y%m%d)/* ./

# Restart original services
cd 4plex-foreclosure-research && ./scripts/start-system.sh
cd ../4plex-investment-platform && docker-compose up -d
```

---

## 🎉 **Migration Complete!**

Congratulations! You now have a unified, powerful 4-Plex Investment Platform that combines the best of both applications into a single, integrated solution.

**Next Steps:**
1. Configure your investment criteria in the `.env` file
2. Start discovering properties across Georgia counties
3. Monitor the automated analysis pipeline
4. Review high-scoring investment opportunities
5. Scale your real estate investment operations

🏠💰 **Your integrated platform is ready to find and analyze 4-plex investment opportunities automatically!**