from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from ...core.config import settings

router = APIRouter()

@router.get('/{filename}')
def serve_upload(filename: str):
    path = Path(settings.upload_dir) / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path, filename=filename)
