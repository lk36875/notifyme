"""
The user_authorization module provides JSON Web Token (JWT) authorization for the NotifyMe API.

This module defines a Flask-JWT-Extended object that provides JWT authorization for the API.
The JWT object is used to protect routes that require authentication, such as the /protected route
in the main blueprint.

This module is imported by the main application factory to provide JWT authorization for the entire API.

Attributes:
    jwt: A Flask-JWT-Extended object that provides JWT authorization for the NotifyMe API.
"""
from flask_jwt_extended import JWTManager

jwt = JWTManager()
