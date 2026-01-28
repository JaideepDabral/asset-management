"""
API Token utilities for external system authentication (Asynchronous)
"""
import secrets
from datetime import datetime, timedelta
from ..database.database import AsyncSessionLocal
from ..models.models import ApiToken
from sqlalchemy.future import select

async def generate_api_token(name: str, created_by: str = None, expires_days: int = None):
    """
    Generate a new API token
    
    Args:
        name: Descriptive name for the token (e.g., "RHEL Server 192.168.1.146")
        created_by: User ID who created the token
        expires_days: Number of days until expiration (None = never expires)
    
    Returns:
        str: The generated token
    """
    # Generate a secure random token (48 bytes = 64 characters in URL-safe base64)
    token = secrets.token_urlsafe(48)
    
    async with AsyncSessionLocal() as db:
        try:
            api_token = ApiToken(
                token=token,
                name=name,
                created_by=created_by,
                expires_at=datetime.now() + timedelta(days=expires_days) if expires_days else None
            )
            db.add(api_token)
            await db.commit()
            print(f"✓ Generated API token for: {name}")
            return token
        except Exception as e:
            print(f"✗ Error generating token: {e}")
            await db.rollback()
            raise

async def validate_api_token(token: str) -> bool:
    """
    Validate if token is active and not expired
    
    Args:
        token: The API token to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(ApiToken).filter(
                    ApiToken.token == token,
                    ApiToken.is_active == True
                )
            )
            api_token = result.scalars().first()
            
            if not api_token:
                return False
            
            # Check expiration
            if api_token.expires_at and api_token.expires_at < datetime.now():
                return False
            
            # Update last_used_at
            api_token.last_used_at = datetime.now()
            await db.commit()
            
            return True
        except Exception as e:
            print(f"Error validating token: {e}")
            return False

async def revoke_api_token(token_id: str):
    """
    Revoke an API token by ID
    
    Args:
        token_id: The ID of the token to revoke
    
    Returns:
        bool: True if revoked, False if not found
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(ApiToken).filter(ApiToken.id == token_id))
            api_token = result.scalars().first()
            if api_token:
                api_token.is_active = False
                await db.commit()
                print(f"✓ Revoked token: {api_token.name}")
                return True
            return False
        except Exception as e:
            print(f"Error revoking token: {e}")
            await db.rollback()
            return False
