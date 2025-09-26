from invenio_records_resources.services import FileLink, FileServiceConfig, RecordLink
from invenio_records_resources.services.files.components import (
    FileContentComponent,
    FileMetadataComponent,
    FileMultipartContentComponent,
    FileProcessorComponent,
)
from invenio_records_resources.services.files.config import (
    FileItem,
    FileList,
    FileSchema,
)
from oarepo_runtime.services.config import PermissionsPresetsConfigMixin

from experiments.records.api import ExperimentsDraft
from experiments.services.files.schema import ExperimentsFileSchema


class ExperimentsWorkflowFilesServiceConfig(
    PermissionsPresetsConfigMixin, FileServiceConfig
):
    """Configuration for workflow files service."""

    service_id = "experiments_workflow_files"

    record_cls = ExperimentsDraft

    schema = ExperimentsFileSchema

    file_schema = FileSchema

    PERMISSIONS_PRESETS = ["everyone"]

    components = [
        FileMetadataComponent,
        FileContentComponent,
        FileMultipartContentComponent,
        FileProcessorComponent,
    ]

    file_result_item_cls = FileItem
    file_result_list_cls = FileList

    @property
    def file_links_list(self):
        return {
            "self": RecordLink(
                "{+api}/experiments/{id}/draft/files",
            ),
        }

    @property
    def file_links_item(self):
        return {
            "commit": FileLink(
                "{+api}/experiments/{id}/draft/files/{key}/commit",
            ),
            "content": FileLink(
                "{+api}/experiments/{id}/draft/files/{key}/content",
            ),
            "preview": FileLink("{+ui}/experiments/{id}/preview/files/{key}/preview"),
            "self": FileLink(
                "{+api}/experiments/{id}/draft/files/{key}",
            ),
        }
