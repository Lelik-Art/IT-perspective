API Base URL: http://localhost:5000/api
{
  "email": "user@example.com",
  "password": "password123"
}
{
  "message": "User registered successfully",
  "token": "jwt_token_here"
}
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
fetch('http://localhost:5000/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
