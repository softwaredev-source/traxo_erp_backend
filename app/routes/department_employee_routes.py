# ============================================================
# FILE: app/routes/department_employee_routes.py
# PURPOSE: All API endpoints for department employees
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.db.database import db
from app.schemas.department_employee_schema import (
    DepartmentEmployeeCreate,
    GetEmployeesByDepartment,
    DepartmentEmployeeUpdate
)
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/department-employees", tags=["Department Employees"])


# ─────────────────────────────────────────────────────────
# ✅ 1. ADD EMPLOYEE TO A DEPARTMENT
#    POST /department-employees/add
# ─────────────────────────────────────────────────────────
@router.post("/add")
def add_department_employee(
    data: DepartmentEmployeeCreate,
    current_user=Depends(get_current_user)     # 🔒 login required
):
    # STEP 1: Validate department_id is a proper MongoDB ObjectId
    try:
        dept_id = ObjectId(data.department_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid department_id format")

    # STEP 2: Check if the department actually exists in DB
    department = db["departments"].find_one({"_id": dept_id})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # STEP 3: Check if employee_code is already used (must be unique)
    existing = db["department_employees"].find_one({
        "employee_code": data.employee_code
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Employee code '{data.employee_code}' already exists"
        )

    # STEP 4: Check if email is already used
    existing_email = db["department_employees"].find_one({
        "email": data.email
    })
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail=f"Employee with email '{data.email}' already exists"
        )

    # STEP 5: Build the employee document to store in MongoDB
    employee = {
        "department_id": dept_id,             # stored as ObjectId
        "name": data.name,
        "email": data.email,
        "mobile_no": data.mobile_no,
        "designation": data.designation,
        "employee_code": data.employee_code,
        "is_active": True                     # default: active employee
    }

    # STEP 6: Insert into "department_employees" collection
    result = db["department_employees"].insert_one(employee)

    # STEP 7: Return success response
    return {
        "message": "Employee added successfully",
        "employee_id": str(result.inserted_id)
    }


# ─────────────────────────────────────────────────────────
# ✅ 2. GET ALL EMPLOYEES OF A DEPARTMENT
#    POST /department-employees/get-by-department
# ─────────────────────────────────────────────────────────
@router.post("/get-by-department")
def get_employees_by_department(
    data: GetEmployeesByDepartment,
    current_user=Depends(get_current_user)
):
    # STEP 1: Validate department_id
    try:
        dept_id = ObjectId(data.department_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid department_id format")

    # STEP 2: Check department exists
    department = db["departments"].find_one({"_id": dept_id})
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # STEP 3: Fetch all employees of this department
    employees = []
    for emp in db["department_employees"].find({"department_id": dept_id}):
        employees.append({
            "_id": str(emp["_id"]),
            "department_id": str(emp.get("department_id")),
            "name": emp.get("name"),
            "email": emp.get("email"),
            "mobile_no": emp.get("mobile_no"),
            "designation": emp.get("designation"),
            "employee_code": emp.get("employee_code"),
            "is_active": emp.get("is_active", True)
        })

    # STEP 4: Return department info + employees list
    return {
        "department_name": department.get("name"),
        "department_id": str(department["_id"]),
        "total_employees": len(employees),
        "employees": employees
    }


# ─────────────────────────────────────────────────────────
# ✅ 3. GET A SINGLE EMPLOYEE BY ID
#    GET /department-employees/{employee_id}
# ─────────────────────────────────────────────────────────
@router.get("/{employee_id}")
def get_employee_by_id(
    employee_id: str,
    current_user=Depends(get_current_user)
):
    # STEP 1: Validate employee_id
    try:
        emp_id = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee_id format")

    # STEP 2: Find the employee
    emp = db["department_employees"].find_one({"_id": emp_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # STEP 3: Return the employee data
    return {
        "_id": str(emp["_id"]),
        "department_id": str(emp.get("department_id")),
        "name": emp.get("name"),
        "email": emp.get("email"),
        "mobile_no": emp.get("mobile_no"),
        "designation": emp.get("designation"),
        "employee_code": emp.get("employee_code"),
        "is_active": emp.get("is_active", True)
    }


# ─────────────────────────────────────────────────────────
# ✅ 4. UPDATE EMPLOYEE DETAILS
#    PUT /department-employees/{employee_id}
# ─────────────────────────────────────────────────────────
@router.put("/{employee_id}")
def update_employee(
    employee_id: str,
    data: DepartmentEmployeeUpdate,
    current_user=Depends(get_current_user)
):
    # STEP 1: Validate employee_id
    try:
        emp_id = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee_id format")

    # STEP 2: Check employee exists
    emp = db["department_employees"].find_one({"_id": emp_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # STEP 3: Build update dict — only include fields that were sent
    # exclude_unset=True means: don't include fields the user didn't send
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # STEP 4: Perform the update
    db["department_employees"].update_one(
        {"_id": emp_id},
        {"$set": update_data}
    )

    return {"message": "Employee updated successfully"}


# ─────────────────────────────────────────────────────────
# ✅ 5. DELETE EMPLOYEE
#    DELETE /department-employees/{employee_id}
# ─────────────────────────────────────────────────────────
@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    current_user=Depends(get_current_user)
):
    # STEP 1: Validate employee_id
    try:
        emp_id = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee_id format")

    # STEP 2: Delete the employee
    result = db["department_employees"].delete_one({"_id": emp_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "Employee deleted successfully"}


# ─────────────────────────────────────────────────────────
# ✅ 6. TOGGLE EMPLOYEE ACTIVE STATUS (activate/deactivate)
#    PUT /department-employees/{employee_id}/toggle-status
# ─────────────────────────────────────────────────────────
@router.put("/{employee_id}/toggle-status")
def toggle_employee_status(
    employee_id: str,
    current_user=Depends(get_current_user)
):
    # STEP 1: Validate employee_id
    try:
        emp_id = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee_id format")

    # STEP 2: Find employee to get current status
    emp = db["department_employees"].find_one({"_id": emp_id})
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # STEP 3: Flip the is_active value
    current_status = emp.get("is_active", True)
    new_status = not current_status   # True → False or False → True

    db["department_employees"].update_one(
        {"_id": emp_id},
        {"$set": {"is_active": new_status}}
    )

    status_label = "activated" if new_status else "deactivated"
    return {"message": f"Employee {status_label} successfully", "is_active": new_status}
