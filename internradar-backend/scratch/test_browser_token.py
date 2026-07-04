import datetime
from jose import jwt, JWTError

secret = "super-secret-key"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTM5NjFlYzBiMjdjYzBiYmMzZTliMDUiLCJlbWFpbCI6InRlc3RfdXNlcl9yYWRhckBnbWFpbC5jb20iLCJleHAiOjE3ODI3NTAzMTh9.9PuZvYlagQgZsjAp315MI46zt43qOTOPM74qvQtRPuo"

try:
    decoded = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
    print("Token decoded successfully with verify_exp=False:", decoded)
except JWTError as e:
    print("JWTError decoding token:", e)
except Exception as e:
    print("Other error:", e)
