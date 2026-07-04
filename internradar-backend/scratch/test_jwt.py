import datetime
from jose import jwt, JWTError

secret = "super-secret-key"
expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)

payload = {
    "sub": "user_123",
    "email": "test@example.com",
    "exp": expire
}

try:
    token = jwt.encode(payload, secret, algorithm="HS256")
    print("Token encoded successfully:", token)
    
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    print("Token decoded successfully:", decoded)
except Exception as e:
    print("Error during JWT operation:", e)
