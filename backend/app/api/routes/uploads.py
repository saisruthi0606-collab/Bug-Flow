from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from ...core.config import settings
from ...models.user import User
from ...utils.auth import get_current_user

router = APIRouter()

@router.get('/{filename}')
def serve_upload(filename: str, current_user: User = Depends(get_current_user)):
    upload_dir = Path(settings.upload_dir).resolve()
    path = (upload_dir / filename).resolve()
    if upload_dir not in path.parents:
        raise HTTPException(status_code=404, detail='File not found')
    if not path.is_file():
        raise HTTPException(status_code=404, detail='File not found')
    return FileResponse(path, filename=filename)
