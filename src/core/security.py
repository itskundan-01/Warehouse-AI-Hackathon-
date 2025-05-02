"""
Security module for WarehouseVision AI.
Provides functionality for password hashing, JWT token generation and verification.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import uuid
import logging

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings import get_settings
from src.database.models import User, UserRole
from src.core.models import TokenData

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Bearer token configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{get_settings().API_V1_PREFIX}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the plain password matches the hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hashed version of the password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the JWT
        expires_delta: Expiration time delta from now
        
    Returns:
        str: Encoded JWT token
    """
    settings = get_settings()
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration time to payload
    to_encode.update({"exp": expire})
    
    # Create the JWT token
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = None
) -> User:
    """
    Get the current user from the JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: User instance
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user_id from token payload
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Create token data object
        token_data = TokenData(
            user_id=uuid.UUID(user_id),
            username=payload.get("username"),
            roles=payload.get("roles", []),
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError:
        raise credentials_exception
    
    # Simple token validation without database access if no db session provided
    if db is None:
        return token_data
    
    # Verify user exists in database
    user_query = await db.execute(select(User).filter(User.id == token_data.user_id))
    user = user_query.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Verify that the current user is active.
    
    Args:
        current_user: User from JWT token
        
    Returns:
        User: User instance if active
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def has_role(required_roles: List[str]):
    """
    Create a dependency that checks if the current user has the required roles.
    
    Args:
        required_roles: List of role names required
        
    Returns:
        callable: Dependency function that validates user roles
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Get the user's role as a string
        user_role = current_user.role.value
        
        # Check if the user's role is in the required roles
        if user_role in required_roles:
            return current_user
                
        # If no matching role found, raise 403
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    return role_checker


class SecurityManager:
    """
    Manages security policies, access control, and authentication rules.
    This class centralizes security-related functionality used by other modules.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SecurityManager.
        
        Args:
            config: Configuration dictionary for security settings
        """
        self.logger = logging.getLogger(__name__)
        
        # Default security configuration
        self.config = {
            'rate_limit_enabled': True,
            'rate_limit_per_minute': 5,
            'failed_login_limit': 3,
            'lockout_duration_minutes': 15,
            'enforce_mfa': False,
            'min_password_length': 8,
            'password_complexity_required': True,
            'access_token_lifetime_minutes': 60,
            'refresh_token_lifetime_days': 7,
            'monitor_suspicious_activity': True,
            'security_audit_logging': True,
        }
        
        # Override with custom config if provided
        if config:
            self.config.update(config)
            
        self.logger.info("SecurityManager initialized with configuration")
        
    def validate_access(
        self, 
        user_id: Optional[str], 
        resource_id: str, 
        action: str,
        access_level: int = 1
    ) -> bool:
        """
        Validate if a user has access to perform an action on a resource.
        
        Args:
            user_id: ID of the user requesting access (or None for anonymous access)
            resource_id: ID of the resource being accessed
            action: The action being performed (e.g., "read", "write", "delete")
            access_level: The minimum access level required for this action
            
        Returns:
            bool: True if access is allowed, False otherwise
        """
        try:
            # For now, implement a simple access control rule
            # In a real implementation, this would check against a proper ACL system
            if user_id is None:
                # Anonymous access only allowed for certain actions and low access levels
                return action.lower() == "read" and access_level <= 1
            
            # TODO: Implement proper access control checks from database
            # This is a placeholder implementation
            return access_level >= 1
            
        except Exception as e:
            self.logger.error(f"Error validating access: {str(e)}")
            # Fail closed - deny access on error
            return False
    
    def log_security_event(
        self, 
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any],
        severity: str = "info"
    ) -> bool:
        """
        Log a security-related event for auditing purposes.
        
        Args:
            event_type: Type of security event (e.g., "login_attempt", "access_denied")
            user_id: ID of the user associated with the event (or None)
            details: Additional details about the event
            severity: Severity level of the event (info, warning, error, critical)
            
        Returns:
            bool: True if logging succeeded, False otherwise
        """
        if not self.config.get('security_audit_logging', True):
            return True
            
        try:
            # Prepare the log entry
            log_entry = {
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": severity,
                "details": details
            }
            
            # Log appropriately based on severity
            if severity == "critical":
                self.logger.critical(f"SECURITY EVENT: {log_entry}")
            elif severity == "error":
                self.logger.error(f"SECURITY EVENT: {log_entry}")
            elif severity == "warning":
                self.logger.warning(f"SECURITY EVENT: {log_entry}")
            else:
                self.logger.info(f"SECURITY EVENT: {log_entry}")
                
            # In a real implementation, this might also:
            # - Write to a dedicated security audit database table
            # - Send alerts for high severity events
            # - Send events to a SIEM system
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
            return False
            
    def is_rate_limited(self, key: str, limit_type: str = "default") -> bool:
        """
        Check if a particular key is currently rate limited.
        
        Args:
            key: The unique key to check rate limiting for (e.g., IP address, user ID)
            limit_type: The type of rate limit to apply
            
        Returns:
            bool: True if rate limited (block request), False otherwise
        """
        if not self.config.get('rate_limit_enabled', True):
            return False
            
        # TODO: Implement proper rate limiting with Redis or similar
        # This is a placeholder implementation that always allows access
        return False
        
    def evaluate_risk_score(self, context: Dict[str, Any]) -> float:
        """
        Calculate a risk score based on the provided context.
        Higher scores indicate higher risk.
        
        Args:
            context: Dictionary containing context about the request/action
            
        Returns:
            float: Risk score between 0.0 (no risk) and 1.0 (highest risk)
        """
        # Simple placeholder implementation
        # In a real system, this would use ML models or rule engines
        
        base_score = 0.1  # Start with low risk
        
        # Check for suspicious factors
        if context.get('user_known', True) == False:
            base_score += 0.3
            
        if context.get('unusual_time', False):
            base_score += 0.2
            
        if context.get('unusual_location', False):
            base_score += 0.3
            
        if context.get('multiple_failed_attempts', False):
            base_score += 0.4
            
        # Cap at 1.0
        return min(base_score, 1.0)