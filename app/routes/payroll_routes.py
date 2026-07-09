from fastapi import APIRouter, HTTPException, Depends

from app.schemas.payroll_schema import (
    PayrollPolicyUpsert,
    LeaveTypeCreate,
    LeaveTypeUpdate,
)
from app.services.payroll_service import (
    get_payroll_policy,
    upsert_payroll_policy,
    create_leave_type,
    get_leave_types_by_company,
    update_leave_type,
    delete_leave_type,
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/admin/companies", tags=["Payroll Policy"])


# ---------------------------------------------------------
# GET /api/v1/admin/companies/{company_id}/payroll-policy
# Safe-Harbor: never 404s, always returns a usable payload.
# ---------------------------------------------------------
@router.get("/{company_id}/payroll-policy")
def fetch_payroll_policy(company_id: str, current_user=Depends(get_current_user)):
    try:
        return get_payroll_policy(company_id)
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------------------------------------------------------
# POST /api/v1/admin/companies/payroll-policy
# Create or Update (Upsert) a company's payroll policy.
# ---------------------------------------------------------
@router.post("/payroll-policy")
def save_payroll_policy(data: PayrollPolicyUpsert, current_user=Depends(get_current_user)):
    try:
        result = upsert_payroll_policy(data.dict())

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ---------------------------------------------------------
# LEAVE TYPES (company_leave_types)
# Not explicitly required in the PDF's API section, but the
# schema was provided, so basic CRUD is wired up the same way.
# ---------------------------------------------------------
@router.post("/leave-types")
def add_leave_type(data: LeaveTypeCreate, current_user=Depends(get_current_user)):
    try:
        result = create_leave_type(data.dict())
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{company_id}/leave-types")
def list_leave_types(company_id: str, current_user=Depends(get_current_user)):
    try:
        return {"leave_types": get_leave_types_by_company(company_id)}
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/leave-types/{leave_type_id}")
def edit_leave_type(leave_type_id: str, data: LeaveTypeUpdate, current_user=Depends(get_current_user)):
    result = update_leave_type(leave_type_id, data.dict())
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.delete("/leave-types/{leave_type_id}")
def remove_leave_type(leave_type_id: str, current_user=Depends(get_current_user)):
    result = delete_leave_type(leave_type_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
