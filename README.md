# ContentMaster AI

A containerized web interface for [danielmiessler/fabric](https://github.com/danielmiessler/fabric) with user authentication and professional content processing.

## Features
- Web-based interface for Fabric CLI with professional content analysis
- User authentication system
- Persistent data storage using Docker volumes
- Support for both YouTube and text analysis
- Multiple analysis patterns (executive summary, key points, etc.)
- Language selection (English/German)
- Interview-ready demonstration showcase

## Prerequisites
- Docker
- Git
- curl (for downloading fabric binary)

## Project Structure
```
contentmaster-ai/
├── Dockerfile
├── requirements.txt
├── ui.py
├── fabric_api.py
├── db_handler.py
├── init_db.py
└── start.sh
```

## Quick Start
1. Clone the repository:
```bash
git clone <your-repository-url>
cd contentmaster-ai
```

2. Build the Docker image:
```bash
docker build -t contentmaster-ai .
```

3. Run the container with a persistent volume:
```bash
docker run -d \
  --name contentmaster-ai \
  -p 8700:8700 \
  -v contentmaster_db:/app/data \
  contentmaster-ai
```

4. Access the application:
- Open your browser and navigate to `http://localhost:8700`
- Login with the predefined credentials:
  - Username: `admin`
  - Password: `admin_secure_password`

## Volume Management
List all volumes:
```bash
docker volume ls
```

Backup the database:
```bash
docker run --rm -v contentmaster_db:/source -v $(pwd):/backup alpine tar -czvf /backup/contentmaster_db_backup.tar.gz -C /source .
```

Restore from backup:
```bash
docker run --rm -v contentmaster_db:/dest -v $(pwd):/backup alpine sh -c "cd /dest && tar -xzvf /backup/contentmaster_db_backup.tar.gz"
```

## Troubleshooting
1. Check container logs:
```bash
docker logs contentmaster-ai
```

2. Access container shell:
```bash
docker exec -it contentmaster-ai bash
```

3. Test Fabric CLI inside container:
```bash
fabric --help
```

4. Test FastAPI endpoint:
```bash
curl -X POST http://localhost:7070/execute/ \
     -H "Content-Type: application/json" \
     -d '{"command":"fabric --help"}'
```

## Port Configuration
The application uses port 8700 for both the web interface and API backend. Make sure this port is available on your host machine.

## Security Notes
- The registration functionality has been disabled for production use
- User credentials are stored with bcrypt hashing
- Database is persisted in a Docker volume
- Default admin credentials should be changed in production

## Container Management
Stop the container:
```bash
docker stop contentmaster-ai
```

Remove the container:
```bash
docker rm contentmaster-ai
```

Remove the volume (will delete all data):
```bash
docker volume rm contentmaster_db
```

## Maintenance
To update the application:
1. Stop the container
2. Build a new image
3. Run a new container (the volume will persist)
```bash
docker stop contentmaster-ai
docker rm contentmaster-ai
docker build -t contentmaster-ai .
docker run -d --name contentmaster-ai -p 8700:8700 -v contentmaster_db:/app/data contentmaster-ai
```