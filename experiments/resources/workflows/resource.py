import json
from typing import Any, Dict
from flask import jsonify, request
from flask_resources import route
from invenio_records_resources.resources import RecordResource
import requests
import time


class ExperimentsWorkflowResource(RecordResource):
    """Experiments workflow resource."""

    FILEPROCESSOR_URL = "http://localhost:8062/api"
    ARGO_URL = "https://localhost:2746/api"

    def create_url_rules(self):
        """Create the URL rules for the workflow resource."""
        routes = self.config.routes
        return [
            route("POST", routes["available"], self.post_available),
            route("POST", routes["create"], self.post_create),
            route("GET", routes["list"], self.get_list_workflows),
            route("GET", routes["detail"], self.get_workflow_detail),
            route("GET", routes["logs"], self.get_workflow_logs)
        ]

    def post_available(self):
        """Proxy POST request to fetch available workflows."""
        try:
            data = request.get_json()

            go_api_url = f"{self.FILEPROCESSOR_URL}/v1/workflows/available"
            response = requests.post(
                go_api_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            return jsonify(response.json()), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to workflow service: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    def post_create(self):
        """Proxy POST request to create workflow."""
        try:
            data = request.get_json()

            go_api_url = f"{self.FILEPROCESSOR_URL}/v1/workflows"
            response = requests.post(
                go_api_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            return jsonify(response.json()), response.status_code

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to workflow service: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    def get_list_workflows(self):
        """Proxy GET request to list record workflows."""
        try:
            if (request.view_args is None):
                raise ValueError('requst view args must be defined')
            record_id = request.view_args.get('record_id') 
            skip = request.args.get('skip', default=0, type=int)
            limit = request.args.get('limit', default=5, type=int)
            status_filter = request.args.get('status', default='', type=str)

            params: Dict[str, Any] = {
                'skip': skip,
                'limit': limit
            }
            if status_filter:
                params['status'] = status_filter

            go_api_url = f"{self.FILEPROCESSOR_URL}/v1/workflows/{record_id}/list"
            response = requests.get(
                go_api_url,
                params=params,
                timeout=30
            )

            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to workflow service: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    def get_workflow_detail(self):
        """Proxy GET request to fetch workflow detail."""
        try:
            if (request.view_args is None):
                raise ValueError('requst view args must be defined')
            workflow_name = request.view_args.get('workflow_name')
            go_api_url = f"{self.FILEPROCESSOR_URL}/v1/workflows/{workflow_name}/detail"
            response = requests.get(
                go_api_url,
                timeout=30
            )

            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to workflow service: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    def get_workflow_logs(self):
        """Proxy GET request to fetch workflow logs from Argo."""
        try:
            if (request.view_args is None):
                raise ValueError('request view args must be defined')
            
            workflow_name = request.view_args.get('workflow_name')
            
            # Build Argo API URL with fixed parameters
            argo_url = f"{self.ARGO_URL}/v1/workflows/argo/{workflow_name}/log"
            params = {
                'logOptions.container': 'main',
                'grep': '',
                'logOptions.follow': 'false'  # Single request, no streaming
            }
            
            # Make request to Argo server
            response = requests.get(
                argo_url,
                params=params,
                stream=True,
                timeout=30,
                verify=False  # Add this if using self-signed certs
            )
            
            if response.status_code != 200:
                return jsonify({"error": f"Argo server returned status {response.status_code}"}), response.status_code
            
            # Collect logs from response - each line is a JSON object
            logs = []
            start_time = time.time()
            timeout_seconds = 30
            
            for line in response.iter_lines(decode_unicode=True):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    break
                    
                if line and line.strip():
                    try:
                        # Each line is a JSON object - parse it directly
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        # Skip malformed JSON
                        continue
            
            return jsonify({
                "logs": logs,
                "total_entries": len(logs),
                "workflow_name": workflow_name
            }), 200
            
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to connect to Argo server: {str(e)}"}), 502
        except Exception as e:
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500
