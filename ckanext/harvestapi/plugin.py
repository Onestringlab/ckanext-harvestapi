import jwt
import requests
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckan.logic import get_action
from flask import Blueprint, jsonify, request
from ckanext.harvest.model import HarvestObject

from ckanext.harvestapi.utils import get_username, get_package_detail


class HarvestapiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic','harvestapi')

    # IBlueprint
    def get_blueprint(self):
        # Method untuk mendaftarkan Blueprint.
        blueprint_harvestapi = Blueprint('harvestapi', __name__,url_prefix='/api/1/harvest')

        @blueprint_harvestapi.route('/welcome-harvest', methods=['GET'])
        def welcome_api():
            """
            Route untuk /welcome_harvest
            """
            return jsonify({
                "message": "Welcome to Harvest API !!!",
                "success": True
            })

        @blueprint_harvestapi.route("/get-harvest-data", methods=["POST"])
        def get_harvest_data():
            """
            Endpoint untuk mendapatkan data harvest
            """
            try:
                # Ambil payload dari request body
                payload = request.get_json()
                if not payload:
                    return jsonify({"success": False, "error": "Request body is required"}), 400

                token = request.headers.get("Authorization")
                _, email = get_username(token)
                username = email.split('@')[0]

                # Ambil parameter dari payload JSON
                query = payload.get('q', '').strip()
                rows = int(payload.get('rows', 10))
                start = int(payload.get('start', 0))
                sort = payload.get('sort', 'prioritas_tahun desc')

                # Periksa panjang query
                if len(query) == 0:  # Jika panjang query 0
                    query = '*:*'
                elif query != '*:*':  # Jika query bukan '*:*', gunakan format pencarian
                    query = f"(title:*{query}* OR notes:*{query}*)"

                # Parameter untuk Solr
                params = {
                    'q': query,  # Query utama
                    'wt': 'json',
                    'rows': rows,
                    'start': start,
                    'sort': sort,
                    'fq': 'dataset_type:harvest' 
                }

                context = {'user': username,'ignore_auth': True}

                # Jalankan package_search
                response = get_action('package_search')(context, params)

                return jsonify({"success": True, "email": email, "data": response})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
            
        @blueprint_harvestapi.route("/get-harvest-data-detail", methods=["POST"])
        def get_harvest_data_detail():
            """
            Endpoint untuk mendapatkan data harvest
            """
            try:
                # Ambil payload dari request body
                payload = request.get_json()
                if not payload:
                    return jsonify({"success": False, "error": "Request body is required"}), 400

                token = request.headers.get("Authorization")
                _, email = get_username(token)
                username = email.split('@')[0]

                # Ambil parameter dari payload JSON
                rows = int(payload.get('rows', 10))
                start = int(payload.get('start', 0))
                harvest_source_id = payload.get('harvest_source_id')

                package_detail = get_package_detail(harvest_source_id)
                owner_org = package_detail["owner_org"]
                # username_capacity = get_username_capacity(username,owner_org)
                print(package_detail)

                # Parameter untuk Solr
                params = {
                    'wt': 'json',
                    'rows': rows,
                    'start': start,
                    'fq': f"harvest_source_id:{harvest_source_id}" 
                }

                context = {'user': username,'ignore_auth': True}

                # Jalankan package_search
                response = get_action('package_search')(context, params)

                return jsonify({"success": True, "email": email, "data": response, "about": package_detail})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        return blueprint_harvestapi


