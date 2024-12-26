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
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

        email = decoded_token.get("email")
        preferred_username = decoded_token.get("preferred_username")

        return preferred_username,email

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token sudah kedaluwarsa"}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({"error": f"Token tidak valid: {str(e)}"}), 400

def get_package_detail(id):
    try:
        if not id:
            raise ValueError("Package ID or name is required")

        context = {"ignore_auth": True} 

        data_dict = {"id": id}

        package_detail = toolkit.get_action("package_show")(context, data_dict)

        return package_detail

    except toolkit.ObjectNotFound:
        raise Exception(f"Package with ID or name '{id}' not found.")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

def get_organization_admin(username, group_id=None):
    data = []
    user = User.get(username)
    if user:
        if user.sysadmin:
            query = '''
                SELECT 
                    g.id, 
                    g.title AS organization_title,
                    g.name AS organization_name
                FROM "group" g
                order by g.name asc
            '''
            result = query_custom(query)
            data = [
                {
                    "user_name": user.name,
                    "user_id": user.id,
                    "organization_id": row[0],
                    "organization_title": row[1],
                    "organization_name": row[2],
                    "capacity": "admin"
                }
                for row in result
            ]

        else:
            query = '''
                SELECT 
                    g.id,
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
                    AND m.capacity = 'admin'
            '''

            result = query_custom(query, {'username': user.name})

            if group_id:
                query += ' AND g.id = :group_id'
                result = query_custom(query, {'username': user.name,'group_id': group_id})

            data = [
                {
                    "user_name": row[1],
                    "user_id": row[2],
                    "organization_id": row[0],
                    "organization_title": row[3],
                    "organization_name": row[4],
                    "capacity": row[5]
                }
                for row in result
            ]

    return data

def has_created_harvest(username):
    capacity = get_organization_admin(username)
    if(len(capacity)>0):
        return True
    return False

def has_managed_harvest(username, group_id):
    capacity = get_organization_admin(username, group_id)
    if(len(capacity)>0):
        return True
    return False
