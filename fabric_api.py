from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI()

class CommandRequest(BaseModel):
    command: str

@app.post("/execute/")
async def execute_command(request: CommandRequest):
    try:
        result = subprocess.run(request.command, shell=True, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}
