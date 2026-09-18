from fastapi import HTTPException, status, Depends
from app.models.user import User, UserRole
from app.auth.jwt_handler import get_current_user

# Role-based access control definitions
ROLE_PERMISSIONS = {
    UserRole.ADMIN.value: {
        "modules": ["*"],
        "actions": ["*"],
    },
    UserRole.INSPECTOR.value: {
        "modules": ["dashboard", "inspections", "field_reports", "violations", "mines", "alerts",
                     "corrective_actions", "documents", "gis", "compliance"],
        "actions": ["read", "create", "update", "verify"],
    },
    UserRole.MINE_OPERATOR.value: {
        "modules": ["dashboard", "mines", "compliance", "documents", "violations", "corrective_actions",
                     "contractors", "production", "field_reports", "workers", "attendance", "alerts", "reports"],
        "actions": ["read", "create", "update"],
    },
    UserRole.ANALYST.value: {
        "modules": ["dashboard", "mines", "compliance", "risk", "reports", "violations",
                     "corrective_actions", "contractors", "production", "alerts", "ai_assistant",
                     "documents", "inspections", "gis", "audit", "workers", "attendance"],
        "actions": ["read"],
    },
    UserRole.VIEWER.value: {
        "modules": ["dashboard", "compliance", "inspections", "violations", "risk", "reports",
                     "mines", "documents", "alerts", "gis", "audit"],
        "actions": ["read"],
    },
}


def check_permission(user: User, module: str, action: str = "read") -> bool:
    """Check if a user has permission to access a module with a given action."""
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    modules = role_perms.get("modules", [])
    actions = role_perms.get("actions", [])

    module_ok = "*" in modules or module in modules
    action_ok = "*" in actions or action in actions

    return module_ok and action_ok


def require_permission(module: str, action: str = "read"):
    """Dependency factory for route-level permission checking."""
    def check(user: User):
        if not check_permission(user, module, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {module}/{action}"
            )
        return user
    return check


def require_role(*roles: str):
    """FastAPI dependency: current user must hold one of the given roles."""
    def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges",
            )
        return user
    return _check


ALL_MODULES = [
    "dashboard", "mines", "compliance", "inspections", "violations", "corrective_actions",
    "contractors", "production", "field_reports", "documents", "risk", "gis",
    "reports", "ai_assistant", "alerts", "audit", "settings", "workers", "attendance",
    "users", "import", "export",
]


def get_user_accessible_modules(role: str) -> list[str]:
    """Get list of modules accessible to a role."""
    perms = ROLE_PERMISSIONS.get(role, {})
    modules = perms.get("modules", [])
    if "*" in modules:
        return ALL_MODULES
    return modules

