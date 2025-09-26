import sys

from flask import g, jsonify, request
from flask_resources import route
from invenio_records_resources.resources import FileResource


class ExperimentsWorkflowFilesResource(FileResource):
    """Resource for anonymous workflow file access using secret keys."""

    def create_url_rules(self):
        """Create the URL rules for the workflow files resource."""
        print("CREATE URL RULES", file=sys.stderr)
        routes = self.config.routes
        return [
            route("POST", routes["read"], self.post_read_file),
            route("POST", routes["write"], self.post_write_files),
        ]

    def post_read_file(self):
        """Read files anonymously using secret key authentication."""
        data = request.get_json()
        if request.view_args is None:
            return jsonify({"error": "request view args must be defined"}), 400

        record_id = request.view_args.get("record_id")

        if not data:
            return jsonify({"error": "JSON payload required"}), 400

        secret_key = data.get("secret_key")
        file_key = data.get("file_key")

        if not secret_key:
            return jsonify({"error": "secret_key is required"}), 400

        if not file_key:
            return jsonify({"error": "file_key must not be empty"}), 400

        result, status_code = self.service.read_file(
            record_id=record_id,
            identity=g.identity,
            secret_key=secret_key,
            file_key=file_key,
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
