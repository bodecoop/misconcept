from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from ..database import get_connection
from ..config import config
from ..schemas.user import TokenData

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password_hash, created_at FROM users WHERE email = :email",
                         {"email": token_data.email})
            user_data = cursor.fetchone()

            if user_data is None:
                raise credentials_exception

            # Create a simple user object
            class User:
                def __init__(self, id, email, password_hash, created_at):
                    self.id = id
                    self.email = email
                    self.password_hash = password_hash
                    self.created_at = created_at

            return User(user_data[0], user_data[1], user_data[2], user_data[3])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")