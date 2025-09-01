# 4-Plex Unified Platform - Port Configuration

## External Ports (Host)
- **Unified API**: 11070 (FastAPI backend)
- **PostgreSQL**: 5434 (Database)
- **Redis**: 6381 (Cache/Session store)
- **Neo4j HTTP**: 7475 (Graph database web interface)
- **Neo4j Bolt**: 7688 (Graph database protocol)
- **Grafana**: 11072 (Monitoring dashboard)

## Internal Docker Ports
- **PostgreSQL**: 5432 (Internal container port)
- **Redis**: 6379 (Internal container port)
- **Neo4j HTTP**: 7474 (Internal container port)
- **Neo4j Bolt**: 7687 (Internal container port)
- **Grafana**: 3000 (Internal container port)

## Access URLs
- **API Documentation**: http://localhost:11070/docs
- **Grafana Dashboard**: http://localhost:11072
- **Neo4j Browser**: http://localhost:7475 (user: neo4j, password: see .env)

## Port Conflict Resolution
The following ports were changed to avoid conflicts with existing services:
- PostgreSQL: 5432 → 5434 (existing PostgreSQL on 5432)
- Redis: 6379 → 6381 (existing Redis on 6379, 6380)
- Neo4j HTTP: 7474 → 7475 (conflict avoidance)
- Neo4j Bolt: 7687 → 7688 (conflict avoidance)