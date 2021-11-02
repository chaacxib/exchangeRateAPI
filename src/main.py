from datetime import timedelta
from jose import JWTError, jwt

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from utils import get_official_gazette_of_the_federation_data, get_banxico_data, get_fixer_data
from auth import Token, TokenData, oauth2_scheme,fake_users_db, get_user, verify_password, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


app = FastAPI()


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def validate_jwt(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      username: str = payload.get("sub")
      if username is None:
          raise credentials_exception
      token_data = TokenData(username=username)
  except JWTError:
      raise credentials_exception

  user = get_user(fake_users_db, username=token_data.username)
  if user is None:
      raise credentials_exception

  return True

@app.get("/")
async def root(authenticated: bool = Depends(validate_jwt)):
  if not authenticated:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )

  result = {'rates':{}}

  result['rates']['diario de la fedearcion'] = get_official_gazette_of_the_federation_data()
  result['rates']['fixer'] = get_fixer_data()
  result['rates']['banxico'] = get_banxico_data()

  return result
