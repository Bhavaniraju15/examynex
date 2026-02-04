from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.auth import SECRET_KEY, ALGORITHM

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Ensure this is an access token, not a refresh token
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "user_id": user_id,
            "role": role
        }

    except JWTError as e:
        if "expired" in str(e).lower():
            raise HTTPException(status_code=401, detail="Token expired - please refresh or login again")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
