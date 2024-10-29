ROLE_PERMISSIONS = {
    "ADMIN": {
        "view": ["ADMIN", "APPROVER", "OWNER", "STAFF", "CLIENT"],
        "create": ["ADMIN", "APPROVER", "OWNER", "STAFF"],
        "edit": ["ADMIN", "APPROVER", "OWNER", "STAFF"],
        "deactivate": ["ADMIN", "APPROVER", "OWNER", "STAFF", "CLIENT"],
    },
    "APPROVER": {
        "view": ["OWNER", "STAFF"],
        "create": ["OWNER", "STAFF"],
        "edit": ["OWNER", "STAFF"],
        "deactivate": ["OWNER", "STAFF"]
    },
    "OWNER": {
        "view": ["STAFF"],
        "create": ["STAFF"],
        "edit": ["STAFF"],
        "deactivate": ["STAFF"]
    },
    "STAFF": {
        # Empty - staff cannot perform actions on other users
    },
}
