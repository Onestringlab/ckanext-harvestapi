import jwt
import json
import requests
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckan.logic import get_action
from flask import Blueprint, jsonify, request
from ckanext.harvest.model import HarvestObject

from ckanext.harvestapi.utils import get_username, get_package_detail, get_organization_admin
from ckanext.harvestapi.utils import has_created_harvest,has_managed_harvest


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
                create_harvest = has_created_harvest(username)

                # Ambil parameter dari payload JSON
                query = payload.get('q', '').strip()
                rows = int(payload.get('rows', 10))
                start = int(payload.get('start', 0))
                sort = payload.get('sort', 'prioritas_tahun desc')
                facet_limit = int(payload.get('facet.limit', 500))
                frequency = payload.get('frequency', '').strip()
                source_type = payload.get('source_type', '').strip()

                # Periksa panjang query
                if len(query) == 0:  # Jika panjang query 0
                    query = '*:*'
                elif query != '*:*':  # Jika query bukan '*:*', gunakan format pencarian
                    query = f"(title:*{query}* OR notes:*{query}*)"

                if frequency:
                    query += f" AND frequency:{frequency}"
                if source_type:
                    query += f" AND source_type:{source_type}"

                # Parameter untuk Solr
                params = {
                    'q': query,  # Query utama
                    'wt': 'json',
                    'rows': rows,
                    'start': start,
                    'sort': sort,
                    'fq': 'dataset_type:harvest',
                    'facet': 'true',
                    'facet.field': ['frequency', 'source_type'],
                    'facet.limit': facet_limit
                }

                context = {'user': username,'ignore_auth': True}

                # Jalankan package_search
                response = get_action('package_search')(context, params)

                return jsonify({"success": True, "email": email, "data": response, "create_harvest": create_harvest })

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

                context = {'user': username,'ignore_auth': True}

                harvest_source = get_action('harvest_source_show')(context, {'id': harvest_source_id})
                owner_org = harvest_source["owner_org"]
                manage_harvest = has_managed_harvest(username, owner_org)

                harvest_jobs = get_action('harvest_job_list')(context, {'source_id': harvest_source['id']})

                return jsonify({"success": True, "email": email, "data": harvest_source,
                                    "manage_harvest": manage_harvest, "harvest_jobs": harvest_jobs})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @blueprint_harvestapi.route("/get-admin-organization", methods=["POST"])
        def get_admin_organization():
            try:
                token = request.headers.get("Authorization")
                _, email = get_username(token)
                username = email.split('@')[0]

                organization_admin = get_organization_admin(username)
                return jsonify({"success": True, "email": email, "data": organization_admin})

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
    
        @blueprint_harvestapi.route("/create-harvest-source", methods=["POST"])
        def create_harvest_source():
            try:
                token = request.headers.get("Authorization")
                _, email = get_username(token)
                username = email.split('@')[0]

                context = {'user': username,'ignore_auth': True}

                payload = request.get_json()
                if not payload:
                    return jsonify({"success": False, "error": "Request body is required"}), 400

                name = payload.get("name")
                title = payload.get("title")
                description = payload.get("description", "")
                source_type = payload.get("source_type")
                url = payload.get("url")
                frequency = payload.get("frequency")
                owner_org = payload.get("owner_org")
                config = payload.get("config", {})
                config_json = json.dumps(config)

                # Menyiapkan data dictionary untuk action
                data_dict = {
                    "name": name,
                    "title": title,
                    "description": description,
                    "source_type": source_type,
                    "url": url,
                    "frequency": frequency,
                    "owner_org": owner_org,
                    "config": config_json
                }

                result = toolkit.get_action("harvest_source_create")(context, data_dict)
                
                return jsonify({
                    "success": True,
                    "message": f"Harvest source '{title}' created successfully.",
                    "data": result
                })
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500




        return blueprint_harvestapi
