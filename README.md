# backend 

## pull and run the docker
docker pull holebro/senao-backend-api  
docker run -d -p 8000:8000 --name api holebro/senao-backend-api


## Create Account

### Endpoint

`POST /api/accounts`

### Description

This endpoint is used to create a new user account.

### Input

```json
{
    "username": "example_username",
    "password": "example_password"
}
```
### Response

```json
# status code 200
{
    "success": true
}
# status code 422
{
    "success": false,
    "reason": "Password must contain at least one lowercase letter"
}
# status code 409
{
    "success": false,
    "reason": "Username already exists"
}
```