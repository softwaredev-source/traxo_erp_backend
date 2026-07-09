from fastapi import Depends, HTTPException
from app.utils.dependencies import get_current_user
from app.constants.roles import SUPER_ADMIN, COMPANY_ADMIN, ALL_ROLES


def require_roles(*allowed_roles):
    """
    Dependency FACTORY. Call it with the roles you want to allow,
    and it hands back a dependency FastAPI can use with Depends(...).

    Example:
        @router.get("/reports", dependencies=[Depends(require_roles(SUPER_ADMIN))])
    """
    invalid = [r for r in allowed_roles if r not in ALL_ROLES]
    if invalid:
        raise ValueError(f"Unknown role(s) passed to require_roles: {invalid}")

    def role_dependency(current_user: dict = Depends(get_current_user)):
        # get_current_user already proved the JWT is valid.
        # Here we additionally check the role written INSIDE that JWT.
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_dependency


# Ready-made shortcuts for the two most common checks
require_super_admin = require_roles(SUPER_ADMIN)
require_super_admin_or_company_admin = require_roles(SUPER_ADMIN, COMPANY_ADMIN)
