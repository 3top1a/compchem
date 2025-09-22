from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AuthenticatedUser

# from invenio_records_permissions.generators import SystemProcess, AnyUser


class ExperimentsPermissionPolicy(RecordPermissionPolicy):
    """experiments.records.api.ExperimentsRecord permissions.
    Values in this class will be merged with permission presets.
    """

    can_search = [AuthenticatedUser()]
    can_read = [AuthenticatedUser()]
    can_create = [AuthenticatedUser()]
    can_update = [AuthenticatedUser()]
    can_delete = [AuthenticatedUser()]
    can_manage = [AuthenticatedUser()]
    can_read_files = [AuthenticatedUser()]
    can_update_files = [AuthenticatedUser()]

    # Additional permissions that might be needed for full functionality
    can_publish = [AuthenticatedUser()]
    can_edit = [AuthenticatedUser()]
    can_review = [AuthenticatedUser()]
    can_read_draft = [AuthenticatedUser()]
    can_update_draft = [AuthenticatedUser()]
    can_delete_draft = [AuthenticatedUser()]
    can_new_version = [AuthenticatedUser()]
    can_search_versions = [AuthenticatedUser()]
