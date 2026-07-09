from fastapi import HTTPException
from app.constants.roles import SUPER_ADMIN


def get_company_filter(current_user: dict) -> dict:
    """
    Implements Section 7 & 8 of the design doc:
      - SUPER_ADMIN -> no filter -> sees every company's data.
      - Everyone else -> locked to their OWN company_id.
      - The company_id is read from the JWT (current_user), NEVER from
        anything the frontend sends in the request body or query string.

    Use it like this in any service function:

        def get_employees(current_user):
            filter_query = get_company_filter(current_user)
            return list(employee_collection.find(filter_query))
    """
    if current_user.get("role") == SUPER_ADMIN:
        return {}

    company_id = current_user.get("company_id")

    if not company_id:
        # A non-super-admin with no company_id is a broken/incomplete
        # account. Fail safe: match nothing rather than leak data.
        return {"company_id": "__no_company_assigned__"}

    return {"company_id": company_id}


def assert_same_company(current_user: dict, resource_company_id) -> None:
    """
    The core tenant-isolation check. Call this right after fetching ANY
    resource (a branch, a department, an employee...) and before letting
    the caller read/edit/delete it.

    - SUPER_ADMIN -> always allowed, no matter whose data it is.
    - Everyone else -> only allowed if the resource's company_id matches
      their OWN company_id (taken from their JWT). Otherwise: 403.
    """
    if current_user.get("role") == SUPER_ADMIN:
        return

    if resource_company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this company's data",
        )
