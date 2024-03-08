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
{
    "success": true
}


{
    "success": false,
    "reason": 
}
```