import logging
import mimetypes
import sys
from typing import Dict, List

from flask import current_app
from invenio_records_resources.services import (
    LinksTemplate,
    Service,
    ServiceSchemaWrapper,
)

from experiments.records.models import ExperimentsWorkflowContext


class ExperimentsWorkflowFilesService(Service):
    """Service for anonymous file access using workflow secret keys."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def record_cls(self):
        """Get the record class."""
        return self.config.record_cls

    @property
    def file_schema(self):
        """Returns the data schema instance.

        The schema can be used for dumping file's metadata or updating them.
        For the creation of a new file, use the `initial_file_schema` property
        as it will include the necessary fields for initiating the file upload.
        """
        return ServiceSchemaWrapper(self, schema=self.config.file_schema)

    def file_result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit."""
        return self.config.file_result_item_cls(*args, **kwargs)

    def file_result_list(self, *args, **kwargs):
        """Create a new instance of the resource list."""
        return self.config.file_result_list_cls(*args, **kwargs)

    def file_links_list_tpl(self, id_):
        """Return a link template for list results."""
        return LinksTemplate(self.config.file_links_list, context={"id": id_})

    def file_links_item_tpl(self, id_):
        """Return a link template for item results."""
        return LinksTemplate(self.config.file_links_item, context={"id": id_})

    def authenticate_request(self, record_id: str, secret_key: str) -> bool:
        """Verify secret key for the given record."""
        self.logger.info(
            f"Authenticating request for record_id={record_id} with secret_key=***"
        )
        try:
            context = ExperimentsWorkflowContext.query.filter_by(
                experiment_id=record_id, secret_key=secret_key
            ).first()

            if context is not None:
                self.logger.info(f"Authentication successful for record_id={record_id}")
                return True
            else:
                self.logger.warning(
                    f"Authentication failed: No context found for record_id={record_id}"
                )
                return False
        except Exception as e:
            self.logger.error(
                f"Authentication error for record_id={record_id}: {str(e)}",
                exc_info=True,
            )
            return False

    def read_files(
        self, identity, record_id: str, secret_key: str, file_keys: List[str]
    ) -> tuple:
        """Generate S3 signed URLs for reading files."""
        self.logger.info(
            f"read_files called for record_id={record_id}, file_keys={file_keys}"
        )

        # Authenticate request
        if not self.authenticate_request(record_id, secret_key):
            self.logger.warning(
                f"Authentication failed for read_files request, record_id={record_id}"
            )
            return {"error": "Invalid secret key or record ID"}, 403

        try:
            # Query draft metadata directly from database
            record = self.record_cls.pid.resolve(record_id, registered_only=False)

            # this has no implementation but is used for some reason, why?
            # self.run_components("list_files", record_id, identity, record)

            files = self.file_result_list(
                self,
                identity,
                results=record.files.values(),
                record=record,
                links_tpl=self.file_links_list_tpl(record_id),
                links_item_tpl=self.file_links_item_tpl(record_id),
            )

            file_urls = {}
            errors = {}

            print("FILESS!!!!!", file=sys.stderr)
            print(files.to_dict(), file=sys.stderr)

            response = {"files": files}
            if errors:
                response["errors"] = errors

            self.logger.info(
                f"read_files completed: {len(file_urls)} file locations returned, {len(errors)} errors"
            )
            return response, 200 if file_urls else 404

        except Exception as e:
            self.logger.error(
                f"Failed to read files for record_id={record_id}: {str(e)}",
                exc_info=True,
            )
            return {"error": f"Failed to read files: {str(e)}"}, 500

    def write_files(self, record_id: str, secret_key: str, files_data: Dict) -> tuple:
        """Write files to S3 for the experiment."""
        self.logger.info(
            f"write_files called for record_id={record_id}, files={list(files_data.keys())}"
        )

        # Authenticate request
        if not self.authenticate_request(record_id, secret_key):
            self.logger.warning(
                f"Authentication failed for write_files request, record_id={record_id}"
            )
            return {"error": "Invalid secret key or record ID"}, 403

        try:
            # For writing, we'll use draft files service as that's typically where files are written
            files_service = current_app.extensions["experiments"].service_draft_files

            written_files = {}
            errors = {}

            for file_key, file_content in files_data.items():
                try:
                    # Determine content type
                    content_type, _ = mimetypes.guess_type(file_key)
                    if not content_type:
                        content_type = "application/octet-stream"

                    # Write file to S3
                    result = self._write_file_to_storage(
                        record_id, file_key, file_content, content_type, files_service
                    )

                    written_files[file_key] = {
                        "status": "uploaded",
                        "size": len(file_content)
                        if isinstance(file_content, (str, bytes))
                        else None,
                        "mimetype": content_type,
                    }

                except Exception as e:
                    self.logger.error(
                        f"Failed to write file {file_key}: {str(e)}", exc_info=True
                    )
                    errors[file_key] = f"Failed to write file: {str(e)}"

            response = {"written_files": written_files}
            if errors:
                response["errors"] = errors

            self.logger.info(
                f"write_files completed: {len(written_files)} files written, {len(errors)} errors"
            )
            return response, 200 if written_files else 400

        except Exception as e:
            self.logger.error(
                f"Failed to write files for record_id={record_id}: {str(e)}",
                exc_info=True,
            )
            return {"error": f"Failed to write files: {str(e)}"}, 500

    def _write_file_to_storage(
        self, record_id: str, file_key: str, content, content_type: str, files_service
    ):
        """Write file content to S3 storage."""
        try:
            # Convert content to proper format
            if isinstance(content, str):
                content_bytes = content.encode("utf-8")
            else:
                content_bytes = content

            # First, initialize the file upload
            file_data = [{"key": file_key, "metadata": {"mimetype": content_type}}]

            init_result = files_service.init_files(
                identity=None, id_=record_id, data=file_data
            )

            # Then, set the file content
            from io import BytesIO

            stream = BytesIO(content_bytes)

            result = files_service.set_file_content(
                identity=None,
                id_=record_id,
                file_key=file_key,
                stream=stream,
                content_length=len(content_bytes),
            )

            # Finally, commit the file
            commit_result = files_service.commit_file(
                identity=None, id_=record_id, file_key=file_key
            )

            return commit_result

        except Exception as e:
            self.logger.error(
                f"Failed to write {file_key} to storage: {str(e)}", exc_info=True
            )
            raise Exception(f"Failed to write to storage: {str(e)}")
