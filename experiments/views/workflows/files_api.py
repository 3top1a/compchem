def create_workflow_files_api_blueprint(app):
    """Create ExperimentsWorkflowFiles blueprint."""
    blueprint = app.extensions["experiments"].resource_workflow_files.as_blueprint()
    blueprint.record_once(init_workflow_files_api_blueprint)

    return blueprint


def init_workflow_files_api_blueprint(state):
    """Init workflow files API blueprint."""
    app = state.app
    ext = app.extensions["experiments"]

    # No need to register service as it's already available via extension
    # The resource accesses the service via current_app.extensions["experiments-workflows"].service_workflow_files