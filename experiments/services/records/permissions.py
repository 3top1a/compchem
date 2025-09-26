from invenio_records_permissions import RecordPermissionPolicy

# from invenio_records_permissions.generators import SystemProcess, AnyUser


class ExperimentsPermissionPolicy(RecordPermissionPolicy):
    """experiments.records.api.ExperimentsRecord permissions.
    Values in this class will be merged with permission presets.
    """

    can_search = []
    can_read = []
    can_create = []
    can_update = []
    can_delete = []
    can_manage = []
    can_read_files = []
    can_update_files = []

    # Additional permissions that might be needed for full functionality
    can_publish = []
    can_edit = []
    can_review = []
    can_read_draft = []
    can_update_draft = []
    can_delete_draft = []
    can_new_version = []
    can_search_versions = []
