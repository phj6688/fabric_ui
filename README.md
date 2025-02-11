# Fabric UI

A containerized web interface for [danielmiessler/fabric](https://github.com/danielmiessler/fabric) with user authentication.

## Features

- Web-based interface for Fabric CLI
- User authentication system
- Persistent data storage using Docker volumes
- Support for both YouTube and text analysis
- Multiple analysis patterns (summarize, extract wisdom, etc.)
- Language selection (English/German)

## Prerequisites

- Docker
- Git
- curl (for downloading fabric binary)

## Project Structure

```
fabric-ui/
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
cd fabric-ui
```

2. Build the Docker image:
```bash
docker build -t fabric-ui .
```

3. Run the container with a persistent volume:
```bash
docker run -d \
  --name fabric-ui \
  -p 8700:8700 \
  -v fabric_db:/app/data \
  fabric-ui
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
docker run --rm -v fabric_db:/source -v $(pwd):/backup alpine tar -czvf /backup/fabric_db_backup.tar.gz -C /source .
```

Restore from backup:
```bash
docker run --rm -v fabric_db:/dest -v $(pwd):/backup alpine sh -c "cd /dest && tar -xzvf /backup/fabric_db_backup.tar.gz"
```

## Troubleshooting

1. Check container logs:
```bash
docker logs fabric-ui
```

2. Access container shell:
```bash
docker exec -it fabric-ui bash
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
docker stop fabric-ui
```

Remove the container:
```bash
docker rm fabric-ui
```

Remove the volume (will delete all data):
```bash
docker volume rm fabric_db
```

## Maintenance

To update the application:
1. Stop the container
2. Build a new image
3. Run a new container (the volume will persist)

```bash
docker stop fabric-ui
docker rm fabric-ui
docker build -t fabric-ui .
docker run -d --name fabric-ui -p 8700:8700 -v fabric_db:/app/data fabric-ui
```