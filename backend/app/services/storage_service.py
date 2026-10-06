import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from app.core.config import settings


class BaseStorageService(ABC):
    """Abstract storage service interface to decouple file persistence from domain logic."""

    @abstractmethod
    async def save_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        subfolder: str = "diseases",
    ) -> str:
        """Saves file bytes and returns a persistent storage identifier / relative path."""
        pass

    @abstractmethod
    async def delete_file(self, relative_path: str) -> bool:
        """Deletes a file given its storage identifier."""
        pass

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> Path:
        """Resolves storage identifier to a filesystem path."""
        pass


class LocalStorageService(BaseStorageService):
    """
    Local filesystem implementation of BaseStorageService.
    Stores uploads under configured settings.STORAGE_DIR while keeping domain entities decoupled.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.STORAGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        subfolder: str = "diseases",
    ) -> str:
        # Extract extension safely
        ext = Path(filename).suffix.lower()
        if not ext:
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            else:
                ext = ".jpg"

        unique_name = f"{uuid.uuid4().hex[:16]}{ext}"
        target_dir = self.base_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / unique_name
        with open(target_file, "wb") as f:
            f.write(file_bytes)

        # Return relative storage path (e.g., 'diseases/abc12345.jpg')
        return f"{subfolder}/{unique_name}"

    async def delete_file(self, relative_path: str) -> bool:
        try:
            target_file = (self.base_dir / relative_path).resolve()
            # Prevent directory traversal attacks
            if self.base_dir not in target_file.parents:
                return False
            if target_file.exists() and target_file.is_file():
                target_file.unlink()
                return True
            return False
        except Exception:
            return False

    def get_absolute_path(self, relative_path: str) -> Path:
        target_file = (self.base_dir / relative_path).resolve()
        return target_file


# Global storage service instance
storage_service = LocalStorageService()
