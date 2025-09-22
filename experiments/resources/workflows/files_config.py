from flask_resources import ResourceConfig


class ExperimentsWorkflowFilesResourceConfig(ResourceConfig):
    """Configuration for workflow files resource."""

    blueprint_name = "experiments_workflow_files"
    url_prefix = "/workflow_files"

    routes = {
        "read": "/read",
        "write": "/write",
    }

