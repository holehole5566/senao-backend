from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Dict
from datetime import datetime, timedelta


app = FastAPI()

account = {}
fail_count = defaultdict(int)
account_blocked = {}


def validate_password(password: str):
    if type(password) != str:
        raise TypeError("Password must be a string")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 32:
        raise ValueError("Password must be at most 32 characters long")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")


def validate_username(username: str):
    if type(username) != str:
        raise TypeError("Username must be a string")
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    if len(username) > 32:
        raise ValueError("Username must be at most 32 characters long")


def validate_exists(username: str):
    if username in account:
        raise ValueError("Username already exists")


def verify_username(username: str, password: str):
    if type(username) != str or type(password) != str:
        raise TypeError("Username and password must be a string")
    if username not in account:
        raise ValueError("Username not found")


def verify_password(username, password):
    if username in account:
        pw = account[username]
        if pw != password:
            raise ValueError("Password is incorrect")
    return True


def check_blocked(username):
    if username in account_blocked:
        wait_time = timedelta(minutes=1)
        if datetime.now() - account_blocked[username] < wait_time:
            raise BaseException("Account is blocked")


@app.post("/api/accounts")
async def create_account(body: Dict):
    try:
        validate_username(body["username"])
        validate_password(body["password"])
    except ValueError as e:
        return JSONResponse(
            status_code=422, content={"success": False, "reason": str(e)}
        )
    except TypeError as e:
        return JSONResponse(
            status_code=422, content={"success": False, "reason": str(e)}
        )
    try:
        validate_exists(body["username"])
    except ValueError as e:
        return JSONResponse(
            status_code=409, content={"success": False, "reason": str(e)}
        )
    account[body["username"]] = body["password"]
    return {"success": True}


@app.post("/api/accounts/verify")
async def verify_account_password(body: Dict):
    """
    Verify the account password.

    Args:
        body (Dict): The request body containing the username and password.

    Returns:
        Union[Dict, JSONResponse]: A dictionary with the success status or a JSONResponse with the error details.
    """
    username = body["username"]
    password = body["password"]
    try:
        verify_username(username, password)
    except ValueError as e:
        return JSONResponse(
            status_code=404, content={"success": False, "reason": str(e)}
        )
    except TypeError as e:
        return JSONResponse(
            status_code=422, content={"success": False, "reason": str(e)}
        )
    # Check if the user should wait before attempting to verify password again
    try:
        check_blocked(username)
    except BaseException as e:
        return JSONResponse(
            status_code=429, content={"success": False, "reason": str(e)}
        )

    try:
        verify_password(username, password)
        if username in fail_count:
            del fail_count[username]
        return {"success": True}
    except ValueError as e:
        fail_count[username] += 1
        if fail_count[username] >= 5:
            account_blocked[username] = datetime.now()
        return JSONResponse(
            status_code=401, content={"success": False, "reason": str(e)}
        )
