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
                token = request.headers.get("Authorization")
                preferred_username, email = get_username(token)
                username = email.split('@')[0]

                params = {'limit': 10, 'offset': 0} 
                context = {"user": username}
                print(context,username)

                # harvest_objects = toolkit.get_action('harvest_object_list')(
                #     context={"user":username}, 
                #     data_dict={}
                # )

                # Kembalikan data dalam format JSON
                return jsonify({
                    "success": True,
                    "result": "harvest_objects"
                })
            except Exception as e:
                # Tangani error dan kembalikan pesan
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500

        return blueprint_harvestapi
