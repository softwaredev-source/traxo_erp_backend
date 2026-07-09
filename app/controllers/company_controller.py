from app.utils.db_helpers import create_company
from app.db.database import company_collection, users_collection
from app.utils.hash import hash_password
from app.constants.roles import COMPANY_ADMIN


def create_company_controller(data):
    company_data = data.dict()

    admin_name = company_data["authorizedPerson"]["fullName"]
    admin_email = company_data["authorizedPerson"]["email"]
    admin_password = company_data.pop("admin_password")  # never store this raw field on the company doc

    # STEP 1: Make sure this email isn't already used by someone else.
    # Checked BEFORE creating the company, so we never end up with an
    # orphan company that has no working login.
    if users_collection.find_one({"email": admin_email}):
        return {"error": f"A user with email '{admin_email}' already exists"}

    # STEP 2: Create the company (this also auto-generates company_id, e.g. "COMP-1001")
    new_company_id = create_company(company_data)

    # STEP 3: Create the Company Admin login for this company
    hashed_pw = hash_password(admin_password)
    users_collection.insert_one({
        "name": admin_name,
        "email": admin_email,
        "password": hashed_pw,
        "role": COMPANY_ADMIN,
        "company_id": new_company_id,
    })

    return {
        "message": "Company onboarded successfully",
        "company_id": new_company_id,
        "company_admin_login": {
            "email": admin_email,
            "note": "Use this email + the admin_password you set, at /auth/login",
        },
    }


def get_companies_controller():
    companies = list(company_collection.find())

    for company in companies:
        company["_id"] = str(company["_id"])   # ✅ FIX

    if len(companies) == 0:
        return {"message": "No companies found"}

    return {"companies": companies}
