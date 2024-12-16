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

def get_package_detail(id):
    try:
        # Pastikan id tidak kosong
        if not id:
            raise ValueError("Package ID or name is required")

        # Konteks untuk user (jika perlu autentikasi, gunakan user terkait)
        context = {"ignore_auth": True}  # Abaikan autentikasi (opsional)

        # Data dictionary untuk aksi package_show
        data_dict = {"id": id}

        # Jalankan aksi package_show
        package_detail = toolkit.get_action("package_show")(context, data_dict)

        # Kembalikan detail package
        return package_detail

    except toolkit.ObjectNotFound:
        # Tangani jika package tidak ditemukan
        raise Exception(f"Package with ID or name '{id}' not found.")
    except Exception as e:
        # Tangani error lainnya
        raise Exception(f"An error occurred: {str(e)}")