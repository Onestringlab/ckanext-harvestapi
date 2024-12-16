import jwt

from flask import jsonify
from ckan.plugins import toolkit

def get_username(jwt_token):
    try:
        # Dekode JWT tanpa memvalidasi signature dan expiration
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

        # Extract the preferred_username
        email = decoded_token.get("email")
        preferred_username = decoded_token.get("preferred_username")

        # Jika sukses, kembalikan decoded token
        return preferred_username,email

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token sudah kedaluwarsa"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Token tidak valid: {str(e)}"}), 400