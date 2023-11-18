import auth
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            token = auth.decodeJWT(credentials.credentials)
            if token == None:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            if token.is_access_token != True:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return token
        elif not self.auto_error:
            return None
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
