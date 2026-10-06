import base64
import io
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from fastapi import HTTPException, status
from PIL import Image

from app.core.config import settings
from app.services.storage_service import storage_service


class AdvisoryImageHandler:
    """
    Validates, decodes, and handles farmer-provided images for advisory questions.
    Ensures images adhere strictly to the project's formats (JPEG, PNG, WebP)
    and size constraints (10MB max).
    Does NOT store raw image binary data into PostgreSQL.
    """

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}

    @classmethod
    def validate_and_decode(
        cls,
        image_base64: Optional[str] = None,
        image_content_type: Optional[str] = None,
        image_filename: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> Optional[Tuple[bytes, str, str, Dict[str, Any]]]:
        """
        Processes image from either base64 payload or an existing storage path reference.
        Returns: (file_bytes, mime_type, filename, image_metadata) or None if no image provided.
        """
        file_bytes: Optional[bytes] = None
        filename: str = image_filename or "farmer_advisory_image.jpg"
        content_type: Optional[str] = image_content_type

        # Case 1: Existing storage path reference
        if image_path and image_path.strip():
            abs_path = storage_service.get_absolute_path(image_path.strip())
            if not abs_path.exists() or not abs_path.is_file():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Referenced image path '{image_path}' not found.",
                )
            # Prevent directory traversal
            storage_base = Path(settings.STORAGE_DIR).resolve()
            if storage_base not in abs_path.parents and abs_path != storage_base:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image path reference.",
                )
            try:
                with open(abs_path, "rb") as f:
                    file_bytes = f.read()
                filename = abs_path.name
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to read referenced image file: {str(e)}",
                )

        # Case 2: Base64 payload
        elif image_base64 and image_base64.strip():
            raw_b64 = image_base64.strip()
            # Handle Data URL format e.g. "data:image/jpeg;base64,...."
            if "," in raw_b64 and raw_b64.startswith("data:"):
                header, raw_b64 = raw_b64.split(",", 1)
                # Try to extract content type from header
                if ";base64" in header and ":" in header:
                    header_type = header.split(":", 1)[1].split(";")[0].strip()
                    if not content_type:
                        content_type = header_type

            try:
                file_bytes = base64.b64decode(raw_b64)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid base64 image encoding: {str(exc)}",
                )

        if not file_bytes:
            return None

        # 1. Validate size
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image uploaded. Please provide a valid crop photo.",
            )

        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uploaded image exceeds maximum allowed size of {max_mb} MB.",
            )

        # 2. Validate extension if filename has one
        ext = Path(filename).suffix.lower()
        if ext and ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image file extension '{ext}'. Allowed: {', '.join(sorted(cls.ALLOWED_EXTENSIONS))}",
            )

        # 3. Validate content type if provided
        if content_type:
            clean_ct = content_type.lower().strip()
            if clean_ct not in cls.ALLOWED_CONTENT_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported image MIME type '{content_type}'. Allowed types: JPEG, PNG, WebP.",
                )

        # 4. Validate image integrity and determine format using PIL
        try:
            pil_img = Image.open(io.BytesIO(file_bytes))
            pil_img.verify()
            # Reopen to read dimensions and format since verify() closes image
            pil_img = Image.open(io.BytesIO(file_bytes))
            width, height = pil_img.size
            img_format = (pil_img.format or "JPEG").upper()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid or corrupted image file: {str(exc)}",
            )

        # Determine normalized MIME type
        if img_format in ("JPEG", "JPG"):
            mime_type = "image/jpeg"
        elif img_format == "PNG":
            mime_type = "image/png"
        elif img_format == "WEBP":
            mime_type = "image/webp"
        else:
            mime_type = content_type or "image/jpeg"

        metadata = {
            "has_image": True,
            "filename": filename,
            "mime_type": mime_type,
            "size_bytes": len(file_bytes),
            "width": width,
            "height": height,
        }

        return file_bytes, mime_type, filename, metadata


image_handler = AdvisoryImageHandler()
