def user_entity(admin_user) -> dict:
    return {
        "id": str(admin_user["_id"]),
        "name": admin_user["name"],
        "email": admin_user["email"],
        "role": admin_user.get("role", "admin"),
        "company_id": admin_user.get("company_id", None),
        "reset_token": admin_user.get("reset_token", None)
    }