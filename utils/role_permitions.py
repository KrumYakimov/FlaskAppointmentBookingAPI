ROLE_PERMISSIONS = {
    "ADMIN": {
        "view": ["ADMIN", "APPROVER", "OWNER", "STAFF", "CLIENT"],
        "register": ["ADMIN", "APPROVER", "OWNER", "STAFF"],
        "edit": ["ADMIN", "APPROVER", "OWNER", "STAFF"],
        "deactivate": ["ADMIN", "APPROVER", "OWNER", "STAFF", "CLIENT"],
    },
    "APPROVER": {
        "view": ["OWNER", "STAFF"],
        "register": ["OWNER", "STAFF"],
        "edit": ["OWNER", "STAFF"],
        "deactivate": ["OWNER", "STAFF"]
    },
    "OWNER": {
        "view": ["STAFF"],
        "register": ["STAFF"],
        "edit": ["STAFF"],
        "deactivate": ["STAFF"]
    },
    "CLIENT": {
        "view": ["CLIENT"],
        "edit": ["CLIENT"],
        "deactivate": ["CLIENT"]
    },
    "STAFF": {
        # Empty - staff cannot perform actions on other users
    },
}
