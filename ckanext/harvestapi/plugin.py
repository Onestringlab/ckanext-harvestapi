import jwt
import requests
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, jsonify, request
from ckanext.harvest.model import HarvestObject

from ckanext.harvestapi.utils import get_username


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

        @blueprint_harvestapi.route("/get-harvest-data", methods=["GET"])
        def get_harvest_data():
            """
            Endpoint untuk mendapatkan data harvest
            """
            try:
                # Query data dari tabel HarvestObject (atau sesuai kebutuhan Anda)
                payload = request.get_json()
                token = request.headers.get("Authorization")
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
                facet_limit = int(payload.get('facet.limit', 500))
                organization = payload.get('organization', '').strip()
                kategori = payload.get('kategori', '').strip()
                prioritas_tahun = payload.get('prioritas_tahun', '').strip()
                tags = payload.get('tags', '').strip()
                res_format = payload.get('res_format', '').strip()

                # Periksa panjang query
                if len(query) == 0:  # Jika panjang query 0
                    query = '*:*'
                elif query != '*:*':  # Jika query bukan '*:*', gunakan format pencarian
                    query = f"(title:*{query}* OR notes:*{query}*)"
                
                if organization:
                    query += f" AND organization:{organization}"
                if kategori:
                    query += f" AND kategori:{kategori}"
                if prioritas_tahun:
                    query += f" AND prioritas_tahun:{prioritas_tahun}"
                if tags:
                    query += f" AND tags:{tags}"
                if res_format:
                    query += f" AND res_format:{res_format}"
                
                # Parameter untuk Solr
                params = {
                    'q': query,  # Query utama
                    'wt': 'json',
                    'rows': rows,
                    'start': start,
                    'sort': sort,
                    'facet': 'true',
                    'facet.field': ['organization', 'kategori', 'prioritas_tahun', 'tags', 'res_format'],
                    'facet.limit': facet_limit
                }

                context = {'user': username,'ignore_auth': True}

                # Jalankan package_search
                response = get_action('package_search')(context, params)


                # Kembalikan data dalam format JSON
                return jsonify({
                    "success": True,
                    "result": response
                })
            except Exception as e:
                # Tangani error dan kembalikan pesan
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        return blueprint_harvestapi
