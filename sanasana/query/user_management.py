from functools import wraps
from flask import abort, request, g
import requests
from flask_login import current_user
import jwt
from jwt import PyJWKClient

# Clerk provides a JWKS endpoint with public keys
JWKS_URL = "https://probable-bulldog-48.clerk.accounts.dev/.well-known/jwks.json"
jwks_client = PyJWKClient(JWKS_URL)


def verify_clerk_token():
    auth_header = request.headers.get("Authorization", None)
    if not auth_header or not auth_header.startswith("Bearer"):
        abort(401, "Missing authorization header")
    
    token = auth_header.split(" ")[1]
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    
    if not signing_key:
        abort(401, "Invalid token header")
    
    try:
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,  # "YOUR-CLERK-API-KEY",  # check audience if configured
            issuer="https://probable-bulldog-48.clerk.accounts.dev"  # your Clerk issuer
        )
        return payload
    except jwt.PyJWTError:
        abort(401, "Invalid token")


def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.current_user or not any(r.name == role_name for r in g.current_user.roles):
                abort(403, "Forbidden")
            return f(*args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not g.current_user:
                abort(403, "Forbidden")            
            user_permissions = {
                perm.name
                for role in g.current_user.roles
                for perm in role.permissions
            }          
            if permission_name not in user_permissions:
                abort(403, "Forbidden")         
            return f(*args, **kwargs)
        return wrapper
    return decorator

