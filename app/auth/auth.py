import bcrypt

from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from app.models import UserBase

SECRET_KEY = "1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 7 * 24 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    username: str
    tipo: str


def get_hash_password(plain_pw: str) -> str:
    pw_bytes = plain_pw.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password=pw_bytes, salt=salt)
    return hashed_pw.decode("utf-8") #Mariadb espera un string en password y bycrip devuelve bytes


def verify_password(plain_pw, hashed_pw) -> bool:
    plain_pw_bytes = plain_pw.encode("utf-8")
    hashed_pw_bytes = hashed_pw.encode("utf-8")
    return bcrypt.checkpw(password=plain_pw_bytes, hashed_password=hashed_pw_bytes)


def create_access_token(user: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode = user.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(user_id=payload.get("user_id"), username=payload.get("username"), tipo=payload.get("tipo"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Tenemos que comprobar si está en la tabla de admins o no
def verify_admin(token: str = Depends(oauth2_scheme)) -> TokenData:
    data: TokenData = decode_token(token)
    if data.tipo != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return data

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    data: TokenData = decode_token(token)
    return data
