import uuid
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.models.schemas import BatchUploadResponse, FileUploadResult, FileMetadata
from app.models.enums import ProcessingStatus
from app.dependencies import get_settings
from app.config import Settings
from app.services.vision_service import build_hardcoded_extraction_result

router = APIRouter(prefix="/v1/files")

# In-memory store for batch results (replace with Redis in production)
_batch_results: dict[str, list[FileUploadResult]] = {}


@router.post("/upload-batch", response_model=BatchUploadResponse)
async def upload_batch(
    files: list[UploadFile],
    settings: Settings = Depends(get_settings),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    batch_id = str(uuid.uuid4())
    results: list[FileUploadResult] = []

    for file in files:
        file_id = str(uuid.uuid4())

        # Read file bytes
        content = await file.read()

        # Edge case: empty file
        if not content or len(content) == 0:
            results.append(FileUploadResult(
                file_id=file_id,
                status=ProcessingStatus.FAILED,
                error="Empty file",
            ))
            continue

        # Size check
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            results.append(FileUploadResult(
                file_id=file_id,
                status=ProcessingStatus.FAILED,
                error=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit",
            ))
            continue

        hardcoded_result = build_hardcoded_extraction_result(page_count=1)
        results.append(FileUploadResult(
            file_id=file_id,
            status=ProcessingStatus.COMPLETED,
            raw_text=hardcoded_result["raw_text"],
            metadata=FileMetadata(
                page_count=hardcoded_result["page_count"],
                confidence_score=hardcoded_result["confidence_score"],
            ),
        ))

    _batch_results[batch_id] = results
    return BatchUploadResponse(batch_id=batch_id, results=results)


@router.get("/batch/{batch_id}", response_model=BatchUploadResponse)
async def get_batch_status(batch_id: str):
    if batch_id not in _batch_results:
        raise HTTPException(status_code=404, detail="Batch not found")
    return BatchUploadResponse(
        batch_id=batch_id, results=_batch_results[batch_id]
    )


