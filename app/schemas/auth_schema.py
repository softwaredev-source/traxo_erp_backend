from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class VendorLoginRequest(BaseModel):
    email: EmailStr
    password: str


class SuperAdminBootstrapSchema(BaseModel):
    """
    Used ONCE to create the very first Super Admin.
    Protected by a secret setup_key (from .env) instead of a login token,
    because no Super Admin exists yet to issue that token.
    """
    name: str
    email: EmailStr
    password: str
    setup_key: str


class CreateUserSchema(BaseModel):
    """
    Used by an EXISTING Super Admin to create any user
    (another Super Admin, a Company Admin, HR, or Employee).
    """
    name: str
    email: EmailStr
    password: str
    role: str  # SUPER_ADMIN, COMPANY_ADMIN, HR, EMPLOYEE
    company_id: Optional[str] = None  # required for every role except SUPER_ADMIN