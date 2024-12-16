import jwt

from flask import jsonify
from ckan.plugins import toolkit
from ckan.model import meta, User

def query_custom(query, params=None):
    """
    Helper function untuk menjalankan query ke database CKAN.
    """
    session = meta.Session
    result = session.execute(query, params or {})
    return result.fetchall()

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

def get_username_capacity(username, group_id=None):
    # Query menggunakan parameterized query untuk keamanan
    query = '''
        SELECT 
            u.name AS user_name, 
            u.id AS user_id, 
            g.title AS organization_title,
            g.name AS organization_name, 
            m.capacity
        FROM "member" m
        JOIN "user" u ON m.table_id = u.id
        JOIN "group" g ON m.group_id = g.id
        WHERE 
            m.state = 'active' 
            AND g.type = 'organization'
            AND u.name = :username
    '''

    result = query_custom(query, {'username': username})

    if group_id:
        query += ' AND g.id = :group_id'
        result = query_custom(query, {'username': username,'group_id': group_id})

    # Konversi hasil query menjadi daftar dictionary
    data = [
        {
            "user_name": row[0],
            "user_id": row[1],
            "organization_title": row[2],
            "organization_name": row[3],
            "capacity": row[4]
        }
        for row in result
    ]

    return data