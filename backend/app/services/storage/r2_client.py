from __future__ import annotations
"""
Cloudflare R2 storage client (S3-compatible).

SECURITY:
- Credentials are read from environment only — never hardcoded, never logged,
  never returned to the frontend.
- boto3 is imported lazily so the module loads even where boto3 is absent;
  when R2 is not configured, all methods degrade gracefully (no exceptions,
  no external calls).

R2_PUBLIC_BASE_URL may be empty: uploads still succeed, but get_public_url()
returns None until a public assets domain is bound.
"""
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_PLACEHOLDER_VALUES = {"", "replace_with_account_id", "replace_with_access_key_id",
                       "replace_with_secret_access_key"}


class R2Client:
    def __init__(self) -> None:
        self._account_id = settings.r2_account_id
        self._access_key_id = settings.r2_access_key_id          # never log
        self._secret_access_key = settings.r2_secret_access_key  # never log
        self.bucket = settings.r2_bucket
        self.public_base_url = (settings.r2_public_base_url or "").rstrip("/")
        self._client = None  # lazy boto3 client

    def is_configured(self) -> bool:
        return all(
            v and v not in _PLACEHOLDER_VALUES
            for v in (self._account_id, self._access_key_id, self._secret_access_key)
        ) and bool(self.bucket)

    def _endpoint(self) -> str:
        return f"https://{self._account_id}.r2.cloudflarestorage.com"

    def _get_client(self):
        if self._client is None:
            import boto3  # lazy — only when configured + actually uploading
            from botocore.config import Config
            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint(),
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
                config=Config(signature_version="s3v4"),
                region_name="auto",
            )
        return self._client

    def get_public_url(self, key: str) -> Optional[str]:
        """Public URL for a key, or None if R2_PUBLIC_BASE_URL is not bound yet."""
        if not self.public_base_url:
            return None
        return f"{self.public_base_url}/{key}"

    def upload_asset(self, file_bytes: bytes, key: str, content_type: str) -> dict:
        """
        Upload bytes to R2 under `key`.
        Returns {ok, key, public_url, size_bytes} on success, or
        {ok: False, message} when not configured / on error (never raises).
        """
        if not self.is_configured():
            return {"ok": False, "configured": False,
                    "message": "R2 not configured — upload skipped"}
        try:
            self._get_client().put_object(
                Bucket=self.bucket, Key=key, Body=file_bytes, ContentType=content_type
            )
            return {
                "ok": True, "configured": True, "key": key,
                "public_url": self.get_public_url(key),  # may be None
                "size_bytes": len(file_bytes),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("R2 upload failed for key=%s: %s", key, exc)
            return {"ok": False, "configured": True, "message": f"upload error: {exc}"}

    def delete_asset(self, key: str) -> dict:
        if not self.is_configured():
            return {"ok": False, "configured": False, "message": "R2 not configured"}
        try:
            self._get_client().delete_object(Bucket=self.bucket, Key=key)
            return {"ok": True, "configured": True, "key": key}
        except Exception as exc:  # noqa: BLE001
            logger.warning("R2 delete failed for key=%s: %s", key, exc)
            return {"ok": False, "configured": True, "message": f"delete error: {exc}"}

    def asset_exists(self, key: str) -> bool:
        if not self.is_configured():
            return False
        try:
            self._get_client().head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:  # noqa: BLE001
            return False

    def status(self) -> dict:
        """Safe status — never exposes credentials."""
        return {
            "r2_configured": self.is_configured(),
            "bucket": self.bucket if self.is_configured() else None,
            "public_base_url_set": bool(self.public_base_url),
            "message": "R2 ready" if self.is_configured() else "R2 not configured",
        }


# Module-level singleton
r2_client = R2Client()
