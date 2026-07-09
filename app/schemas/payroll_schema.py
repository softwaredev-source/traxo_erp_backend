from pydantic import BaseModel, Field
from typing import Optional, Literal


# =========================================================
# 1) PAYROLL POLICY  -> collection: payroll_policy
# =========================================================

class PayrollPolicyUpsert(BaseModel):
    """
    Used for POST /api/v1/admin/companies/payroll-policy (Create OR Update).
    Field limits below come directly from the PDF's Field Mapping Matrix.
    If the admin doesn't send a field, the Default value from the matrix kicks in.
    """
    company_id: str

    basic_percentage: float = Field(
        default=50.0, ge=10.0, le=100.0,
        description="Min 10.0, Max 100.0, Default 50.0"
    )
    hra_percentage: float = Field(
        default=20.0, ge=0.0, le=100.0,
        description="Min 0.0, Max 100.0, Default 20.0"
    )
    is_cap_pf_at_statutory_ceiling: bool = Field(
        default=True,
        description="True = cap PF base at ₹15,000 ceiling. False = PF on full basic pay."
    )
    monthly_allowed_paid_leaves: int = Field(
        default=1, ge=0, le=31,
        description="Min 0, Max 31, Default 1"
    )


class PayrollPolicyResponse(BaseModel):
    """Shape returned by GET. Same shape is used for the safe-harbor default payload."""
    company_id: str
    basic_percentage: float
    hra_percentage: float
    is_cap_pf_at_statutory_ceiling: bool
    monthly_allowed_paid_leaves: int


# =========================================================
# 2) COMPANY LEAVE TYPES -> collection: company_leave_types
# =========================================================

class LeaveTypeCreate(BaseModel):
    company_id: str
    leave_type_name: str  # e.g. "Casual Leave", "Sick Leave", "Earned Leave"
    annual_allocation: int = Field(..., ge=0, description="Total days given per year, e.g. 12 or 15")
    accrual_type: Literal["MONTHLY", "YEARLY"] = Field(
        ..., description="MONTHLY = credited 1/month, YEARLY = all upfront"
    )
    is_encashable: bool = Field(default=False)
    max_carry_forward: int = Field(default=0, ge=0, description="Max unused days rolled to next year")


class LeaveTypeUpdate(BaseModel):
    """All optional -> only the fields the admin actually sends get changed."""
    leave_type_name: Optional[str] = None
    annual_allocation: Optional[int] = Field(default=None, ge=0)
    accrual_type: Optional[Literal["MONTHLY", "YEARLY"]] = None
    is_encashable: Optional[bool] = None
    max_carry_forward: Optional[int] = Field(default=None, ge=0)


class LeaveTypeResponse(BaseModel):
    id: str
    company_id: str
    leave_type_name: str
    annual_allocation: int
    accrual_type: str
    is_encashable: bool
    max_carry_forward: int
