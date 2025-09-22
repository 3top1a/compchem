import mimetypes
from typing import Dict, List

from flask import current_app
from invenio_records_resources.services import Service

from experiments.records.models import ExperimentsWorkflowContext


class ExperimentsWorkflowFilesService(Service):
    """Service for anonymous file access using workflow secret keys."""

    def authenticate_request(self, record_id: str, secret_key: str) -> bool:
        """Verify secret key for the given record."""
        try:
            context = ExperimentsWorkflowContext.query.filter_by(
                experiment_id=record_id,
                secret_key=secret_key
            ).first()

            return context is not None
        except Exception:
            return False

    def read_files(self, record_id: str, secret_key: str, file_keys: List[str]) -> tuple:
        """Generate S3 signed URLs for reading files."""
        # Authenticate request
        if not self.authenticate_request(record_id, secret_key):
            return {"error": "Invalid secret key or record ID"}, 403

        try:
            # Get the experiments service to access files
            experiments_service = current_app.extensions["experiments"].service_records

            # Read the record using the PID
            record = experiments_service.read(identity=None, id_=record_id)

            # Get files from the record
            files_entries = record.data.get('files', {}).get('entries', {})

            signed_urls = {}
            errors = {}

            for file_key in file_keys:
                try:
                    # Check if file exists in the record
                    if file_key not in files_entries:
                        errors[file_key] = "File not found in experiment"
                        continue

                    # Generate signed URL for the file
                    signed_url = self._generate_s3_signed_url(record_id, file_key)
                    signed_urls[file_key] = {
                        "signed_url": signed_url,
                        "size": files_entries[file_key].get('size'),
                        "mimetype": files_entries[file_key].get('mimetype')
                    }

                except Exception as e:
                    errors[file_key] = f"Failed to generate signed URL: {str(e)}"

            response = {"files": signed_urls}
            if errors:
                response["errors"] = errors

            return response, 200 if signed_urls else 404

        except Exception as e:
            return {"error": f"Failed to read files: {str(e)}"}, 500

    def write_files(self, record_id: str, secret_key: str, files_data: Dict) -> tuple:
        """Write files to S3 for the experiment."""
        # Authenticate request
        if not self.authenticate_request(record_id, secret_key):
            return {"error": "Invalid secret key or record ID"}, 403

        try:
            # Get the experiments service
            experiments_service = current_app.extensions["experiments"].service_records

            # Read the record using the PID to verify it exists
            record = experiments_service.read(identity=None, id_=record_id)

            written_files = {}
            errors = {}

            for file_key, file_content in files_data.items():
                try:
                    # Determine content type
                    content_type, _ = mimetypes.guess_type(file_key)
                    if not content_type:
                        content_type = 'application/octet-stream'

                    # Write file to S3
                    result = self._write_file_to_storage(
                        record_id,
                        file_key,
                        file_content,
                        content_type
                    )

                    written_files[file_key] = {
                        "status": "uploaded",
                        "size": len(file_content) if isinstance(file_content, (str, bytes)) else None,
                        "mimetype": content_type
                    }

                except Exception as e:
                    errors[file_key] = f"Failed to write file: {str(e)}"

            response = {"written_files": written_files}
            if errors:
                response["errors"] = errors

            return response, 200 if written_files else 400

        except Exception as e:
            return {"error": f"Failed to write files: {str(e)}"}, 500

    def _generate_s3_signed_url(self, record_id: str, file_key: str) -> str:
        """Generate S3 signed URL for file access."""
        try:
            # Get the experiments files service
            files_service = current_app.extensions["experiments"].service_files

            # Get the file object
            file_obj = files_service.read_file_metadata(
                identity=None,
                id_=record_id,
                file_key=file_key
            )

            # Generate presigned URL using the file service's S3 integration
            # This will depend on your current S3 setup
            signed_url = files_service.get_download_url(
                identity=None,
                id_=record_id,
                file_key=file_key,
                expires_in=3600  # 1 hour expiration
            )

            return signed_url

        except Exception as e:
            raise Exception(f"Failed to generate S3 signed URL: {str(e)}")

    def _write_file_to_storage(self, record_id: str, file_key: str, content, content_type: str):
        """Write file content to S3 storage."""
        try:
            # Get the experiments files service
            files_service = current_app.extensions["experiments"].service_files

            # Convert content to proper format
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content

            # Create file in the record using the files service
            result = files_service.create_file(
                identity=None,
                id_=record_id,
                file_key=file_key,
                content=content_bytes,
                content_type=content_type
            )

            return result

        except Exception as e:
            raise Exception(f"Failed to write to storage: {str(e)}")