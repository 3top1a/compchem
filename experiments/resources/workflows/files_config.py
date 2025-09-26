from invenio_records_resources.resources import FileResourceConfig


class ExperimentsWorkflowFilesResourceConfig(FileResourceConfig):
    """Configuration for workflow files resource."""

    blueprint_name = "experiments_workflow_files"
    url_prefix = "/workflow_files/"

    routes = {
        "read": "/<record_id>/read",
        "write": "/<record_id>/write",
    }
