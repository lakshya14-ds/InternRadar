from app.routers.auth import decode_token
from jose import JWTError

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2YTM5NjFlYzBiMjdjYzBiYmMzZTliMDUiLCJlbWFpbCI6InRlc3RfdXNlcl9yYWRhckBnbWFpbC5jb20iLCJleHAiOjE3ODI3NTAzMTh9.9PuZvYlagQgZsjAp315MI46zt43qOTOPM74qvQtRPuo"

try:
    data = decode_token(token)
    print("Verification SUCCESS:")
    print("user_id:", data.user_id)
    print("email:", data.email)
except Exception as e:
    print("Verification FAILED:", e)
