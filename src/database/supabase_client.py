"""
Supabase Client for PCA Agent.

Provides access to Supabase features beyond PostgreSQL:
- Authentication (SSO, OAuth)
- Storage (file uploads)
- Realtime subscriptions
"""

import os
from typing import Optional
from loguru import logger

# Optional: Install with `pip install supabase`
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase-py not installed. Install with: pip install supabase")


class SupabaseClient:
    """Wrapper for Supabase client with lazy initialization."""
    
    _instance: Optional["SupabaseClient"] = None
    _client: Optional["Client"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    @property
    def client(self) -> Optional["Client"]:
        """Get Supabase client (lazy initialization)."""
        if not SUPABASE_AVAILABLE:
            logger.error("Supabase client not available. Install with: pip install supabase")
            return None
        
        if self._client is None and self.url and self.anon_key:
            try:
                self._client = create_client(self.url, self.anon_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                return None
        
        return self._client
    
    def is_available(self) -> bool:
        """Check if Supabase is configured and available."""
        return bool(self.url and self.anon_key and SUPABASE_AVAILABLE)
    
    # --- Auth Helpers ---
    def sign_up(self, email: str, password: str) -> dict:
        """Sign up a new user."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        return self.client.auth.sign_up({"email": email, "password": password})
    
    def sign_in(self, email: str, password: str) -> dict:
        """Sign in an existing user."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        return self.client.auth.sign_in_with_password({"email": email, "password": password})
    
    def sign_out(self) -> None:
        """Sign out the current user."""
        if self.client:
            self.client.auth.sign_out()
    
    def get_user(self):
        """Get the current authenticated user."""
        if not self.client:
            return None
        return self.client.auth.get_user()
    
    # --- Storage Helpers ---
    def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = "application/octet-stream") -> dict:
        """Upload a file to Supabase Storage."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        return self.client.storage.from_(bucket).upload(path, file_data, {"content-type": content_type})
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file in storage."""
        if not self.client:
            raise RuntimeError("Supabase client not initialized")
        return self.client.storage.from_(bucket).get_public_url(path)


# Global instance
def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance."""
    return SupabaseClient()
