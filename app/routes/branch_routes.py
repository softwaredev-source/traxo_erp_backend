
# from fastapi import APIRouter
# from app.db.database import db
# from bson import ObjectId

# router = APIRouter(prefix="/branches", tags=["Branches"])


# # CREATE BRANCH
# @router.post("/")
# def create_branch(name: str, location: str, company_id: str):
#     branch = {
#         "name": name,
#         "location": location,
#         "company_id": company_id
#     }

#     result = db["branches"].insert_one(branch)
#     branch["_id"] = str(result.inserted_id)

#     return branch


# # GET ALL BRANCHES
# @router.get("/")
# def get_branches():
#     branches = []

#     for branch in db["branches"].find():
#         branch["_id"] = str(branch["_id"])
#         branches.append(branch)

#     return branches


# # DELETE BRANCH
# @router.delete("/{branch_id}")
# def delete_branch(branch_id: str):
#     result = db["branches"].delete_one({"_id": ObjectId(branch_id)})

#     if result.deleted_count == 0:
#         return {"error": "Branch not found"}

#     return {"message": "Deleted successfully"}








from fastapi import APIRouter, HTTPException,Depends
from bson import ObjectId
from app.db.database import db
from app.models.branch import BranchCreateSchema 
from app.schemas.branch_schema import BranchByCompany
from app.utils.dependencies import get_current_user
from app.utils.tenant_scope import assert_same_company
from app.constants.roles import SUPER_ADMIN

router = APIRouter(prefix="/branches", tags=["Branches"])


# ✅ CREATE BRANCH
@router.post("/")
def create_branch(
    data: BranchCreateSchema,
    current_user=Depends(get_current_user)
):
    # A Super Admin may create a branch for ANY company (must specify which).
    # Everyone else can only ever create a branch for THEIR OWN company --
    # even if they send a different company_id in the request body, it's ignored.
    if current_user.get("role") == SUPER_ADMIN:
        target_company_id = data.company_id
        if not target_company_id:
            raise HTTPException(status_code=400, detail="company_id is required")
    else:
        target_company_id = current_user.get("company_id")

    company = db["companies"].find_one({"company_id": target_company_id})

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    branch = {
        "name": data.name,
        "location": data.location,
        "lattitude": data.lattitude,
        "longitude": data.longitude,
        "radius": data.radius,
        "company_id": target_company_id
    }

    result = db["branches"].insert_one(branch)

    return {
        "_id": str(result.inserted_id),
        "name": data.name,
        "location": data.location,
        "lattitude": data.lattitude,
        "longitude": data.longitude,
        "radius": data.radius,
        "company_id": target_company_id
    }


# # ✅ GET ALL BRANCHES

@router.post("/get-by-company")
def get_branches(
    data: BranchByCompany,
    current_user=Depends(get_current_user)
):
    # Super Admin can look up any company's branches (uses what they send).
    # Everyone else always gets THEIR OWN company's branches, regardless
    # of what company_id they put in the request body.
    if current_user.get("role") == SUPER_ADMIN:
        target_company_id = data.company_id
    else:
        target_company_id = current_user.get("company_id")

    branches = []

    for branch in db["branches"].find({"company_id": target_company_id}):
        branches.append({
            "_id": str(branch["_id"]),
            "name": branch.get("name"),
            "location": branch.get("location"),
            "company_id": branch.get("company_id")
        })

    return {"branches": branches}



# ✅ DELETE BRANCH
@router.delete("/{branch_id}")
def delete_branch(branch_id: str, current_user=Depends(get_current_user)):
    try:
        branch = db["branches"].find_one({"_id": ObjectId(branch_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid branch_id format")

    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Ownership check: only Super Admin, or the branch's OWN company, may delete it
    assert_same_company(current_user, branch.get("company_id"))

    db["branches"].delete_one({"_id": ObjectId(branch_id)})

    return {"message": "Deleted successfully"}