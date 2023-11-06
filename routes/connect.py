# routes/connect.py
from flask import Blueprint, request, jsonify
import requests

bp = Blueprint('connect', __name__)
from urllib.parse import urlparse, parse_qs

# Define your query parameters
query_parameters = {
    'wargame': 'wargame',
    'access': 'access',
    'host': 'host',
}

def extract_last_segment_and_base_url(url, query_parameters):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    wargame_param = query_params.get(query_parameters['wargame'], [None])[0]
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    last_segment = query_params.get(query_parameters['access'], [None])[0]

    return {
        "host": base_url,
        "access": last_segment,
        "wargame": wargame_param
    }

# Pass the json data as a function argument
@bp.route("/connect/", methods=["POST"])
def connect_wargame():
    data = request.get_json()
    params = extract_last_segment_and_base_url(data, query_parameters)
    wargame = params.get('wargame')
    access = params.get('access')
    host = params.get('host')

    if not (wargame and access and host):
        return jsonify({"msg": 'ok', "data": []})

    try:
        response = requests.get(f"{host}/{wargame}/last")
        response.raise_for_status()
        response_data = response.json()

        allForces = response_data.get('data', [])[0].get('data', {}).get('forces', {}).get('forces', [])
        role = None
        force = None

        for force in allForces:
            role = next((roleItem for roleItem in force.get('roles', []) if roleItem.get('roleId') == access), None)
            if role:
                break

        if not role or not force:
            return jsonify({"error": "There is no player matching the provided criteria"}), 400

        force['wargame'] = wargame
        force['host'] = host
        force['roles'] = role

        response_data = {
            "msg": 'ok',
            "data": force
        }

        return jsonify(response_data)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch data"}), 400

    return jsonify([])

