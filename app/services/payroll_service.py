from bson import ObjectId
from bson.errors import InvalidId

from app.db.database import (
    payroll_policy_collection,
    company_leave_types_collection,
    company_collection,
)

# ---------------------------------------------------------
# These are the exact "factory defaults" from the PDF matrix.
# Used ONLY when a company has never saved a policy yet.
# ---------------------------------------------------------
DEFAULT_PAYROLL_POLICY = {
    "basic_percentage": 50.0,
    "hra_percentage": 20.0,
    "is_cap_pf_at_statutory_ceiling": True,
    "monthly_allowed_paid_leaves": 1,
}


def _to_object_id(leave_type_or_branch_id: str) -> ObjectId:
    """Still used for leave_type_id / branch_id, which remain Mongo ObjectIds."""
    try:
        return ObjectId(leave_type_or_branch_id)
    except (InvalidId, TypeError):
        raise ValueError("Invalid id format")


# =========================================================
# PAYROLL POLICY
# =========================================================

def get_payroll_policy(company_id: str) -> dict:
    """
    GET logic.
    Critical Safe-Harbor Rule (from PDF):
    If no record exists for this company_id, DO NOT 404.
    Return the default fallback payload instead, so downstream
    payroll calculation services never break.
    """
    policy = payroll_policy_collection.find_one({"company_id": company_id})

    if not policy:
        # No custom policy saved yet -> hand back the safe defaults
        return {"company_id": company_id, **DEFAULT_PAYROLL_POLICY}

    policy["company_id"] = company_id
    policy.pop("_id", None)
    return policy


def upsert_payroll_policy(data: dict) -> dict:
    """
    POST logic (Create OR Update = Upsert).
    Pydantic (the schema) has already checked the min/max limits
    before this function ever runs.
    """
    company_id = data["company_id"]

    # Make sure the company actually exists -- looked up by the readable
    # company_id field now (e.g. "COMP-1001"), not a Mongo ObjectId.
    company = company_collection.find_one({"company_id": company_id})
    if not company:
        return {"error": "Company not found"}

    update_fields = {
        "basic_percentage": data["basic_percentage"],
        "hra_percentage": data["hra_percentage"],
        "is_cap_pf_at_statutory_ceiling": bool(data["is_cap_pf_at_statutory_ceiling"]),
        "monthly_allowed_paid_leaves": data["monthly_allowed_paid_leaves"],
    }

    payroll_policy_collection.update_one(
        {"company_id": company_id},
        {"$set": update_fields, "$setOnInsert": {"company_id": company_id}},
        upsert=True,
    )

    return {"message": "Payroll policy saved successfully", "company_id": company_id, **update_fields}


# =========================================================
# COMPANY LEAVE TYPES
# =========================================================

def create_leave_type(data: dict) -> dict:
    company = company_collection.find_one({"company_id": data["company_id"]})
    if not company:
        return {"error": "Company not found"}

    leave_type = {
        "company_id": data["company_id"],
        "leave_type_name": data["leave_type_name"],
        "annual_allocation": data["annual_allocation"],
        "accrual_type": data["accrual_type"],
        "is_encashable": data.get("is_encashable", False),
        "max_carry_forward": data.get("max_carry_forward", 0),
    }

    result = company_leave_types_collection.insert_one(leave_type)
    leave_type["id"] = str(result.inserted_id)
    leave_type.pop("_id", None)
    return leave_type


def get_leave_types_by_company(company_id: str) -> list:
    leave_types = list(company_leave_types_collection.find({"company_id": company_id}))
    for lt in leave_types:
        lt["id"] = str(lt["_id"])
        lt.pop("_id", None)
    return leave_types


def update_leave_type(leave_type_id: str, data: dict) -> dict:
    try:
        object_id = ObjectId(leave_type_id)
    except (InvalidId, TypeError):
        return {"error": "Invalid leave_type_id format"}

    # Only keep fields the admin actually sent (drop the Nones)
    update_fields = {k: v for k, v in data.items() if v is not None}

    if not update_fields:
        return {"error": "No fields provided to update"}

    result = company_leave_types_collection.update_one(
        {"_id": object_id}, {"$set": update_fields}
    )

    if result.matched_count == 0:
        return {"error": "Leave type not found"}

    return {"message": "Leave type updated successfully"}


def delete_leave_type(leave_type_id: str) -> dict:
    try:
        object_id = ObjectId(leave_type_id)
    except (InvalidId, TypeError):
        return {"error": "Invalid leave_type_id format"}

    result = company_leave_types_collection.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        return {"error": "Leave type not found"}

    return {"message": "Leave type deleted successfully"}
