from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import logging
import secrets
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('/app/data/logs', 'fabric_api.log')) if os.path.exists('/app/data/logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Generate an API key if one doesn't exist (or use from environment)
API_KEY = os.environ.get("FABRIC_API_KEY") or secrets.token_urlsafe(32)
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="Fabric CLI API", 
              description="API for executing Fabric CLI commands",
              version="1.0.0")

# Add CORS middleware - restrict to the Flask app in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8700"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class CommandRequest(BaseModel):
    """Model for command execution request."""
    command: str

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key for secured endpoints."""
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API key")

@app.on_event("startup")
async def startup_event():
    """Log API key on startup (only for development)."""
    logger.info(f"Fabric API service started. API Key: {API_KEY}")

@app.post("/execute/")
async def execute_command(
    request: CommandRequest,
    api_key: str = Depends(get_api_key)
):
    """Execute a fabric CLI command."""
    try:
        # Log the incoming command (sanitize sensitive information if needed)
        logger.info(f"Executing command: {request.command}")
        
        # Add a timeout to prevent hanging commands
        result = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        logger.info(f"Command completed with return code: {result.returncode}")
        
        if result.returncode != 0:
            logger.warning(f"Command error: {result.stderr}")
            
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        logger.error("Command execution timed out")
        return {
            "stdout": "",
            "stderr": "Command execution timed out after 60 seconds",
            "returncode": 124
        }
        
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": 1
        }
