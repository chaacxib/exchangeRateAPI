import os

from mangum import Mangum
from datetime import timedelta, datetime
from jose import JWTError, jwt

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from utils import get_official_gazette_of_the_federation_data, get_banxico_data, get_fixer_data, max_requests
from database import User, Request
from auth import Token, TokenData, oauth2_scheme, get_user, verify_password, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
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

  user = get_user(username=token_data.username)
  if user is None:
      raise credentials_exception

  return user.username

@app.get("/")
async def root(username: str = Depends(validate_jwt)):
  if max_requests(username=username):
    raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Maximum requests reached, try again in 30 minutes"
    )

  result = {'rates':{}}

  result['rates']['diario de la fedearcion'] = get_official_gazette_of_the_federation_data()
  result['rates']['fixer'] = get_fixer_data()
  result['rates']['banxico'] = get_banxico_data()

  req = Request(username=username, datetime=datetime.utcnow())
  req.save()

  return result

if not User.exists():
        User.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
        user = User(username=os.environ['TEST_USER_NAME'], hashed_password=os.environ['TEST_USER_PASSWORD'])
        user.save()

if not Request.exists():
        Request.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

handler = Mangum(app)
