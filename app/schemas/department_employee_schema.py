from pydantic import BaseModel, EmailStr
from typing import Optional


# ✅ Schema for ADDING a new employee to a department
class DepartmentEmployeeCreate(BaseModel):
    department_id: str        # which department this employee belongs to
    name: str                 # employee full name
    email: EmailStr           # employee email (validated automatically)
    mobile_no: str            # employee mobile number
    designation: str          # e.g. "Software Engineer", "Accountant"
    employee_code: str        # unique code like "EMP001"


# ✅ Schema for GETTING employees by department
class GetEmployeesByDepartment(BaseModel):
    department_id: str        # we send this to fetch all employees of a dept


# ✅ Schema for UPDATING employee details (all fields optional)
class DepartmentEmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_no: Optional[str] = None
    designation: Optional[str] = None
    employee_code: Optional[str] = None
