from flask import current_app, g, jsonify, request
from flask_resources import Resource, route


class ExperimentsWorkflowFilesResource(Resource):
    """Resource for anonymous workflow file access using secret keys."""

    @property
    def service(self):
        """Get the workflow files service."""
        return current_app.extensions["experiments-workflows"].service_workflow_files

    def create_url_rules(self):
        """Create the URL rules for the workflow files resource."""
        routes = self.config.routes
        return [
            route("POST", routes["read"], self.post_read_files),
            route("POST", routes["write"], self.post_write_files),
        ]

    def post_read_files(self):
        """Read files anonymously using secret key authentication."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON payload required"}), 400

        record_id = data.get("record_id")
        secret_key = data.get("secret_key")
        file_keys = data.get("file_keys", [])

        if not record_id or not secret_key:
            return jsonify({"error": "record_id and secret_key are required"}), 400

        if not file_keys or not isinstance(file_keys, list):
            return jsonify({"error": "file_keys must be a non-empty list"}), 400

        result, status_code = self.service.read_files(
            record_id=record_id,
            identity=g.identity,
            secret_key=secret_key,
            file_keys=file_keys,
        )

        return jsonify(result), status_code

    def post_write_files(self):
        """Write files anonymously using secret key authentication."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "JSON payload required"}), 400

        record_id = data.get("record_id")
        secret_key = data.get("secret_key")
        files_data = data.get("files", {})

        if not record_id or not secret_key:
            return jsonify({"error": "record_id and secret_key are required"}), 400

        if not files_data or not isinstance(files_data, dict):
            return jsonify({"error": "files must be a non-empty dictionary"}), 400

        result, status_code = self.service.write_files(
            record_id=record_id, secret_key=secret_key, files_data=files_data
        )

        return jsonify(result), status_code
