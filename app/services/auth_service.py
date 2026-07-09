from app.db.database import users_collection
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_token
from app.core.config import SUPER_ADMIN_SETUP_KEY
from app.constants.roles import SUPER_ADMIN, ALL_ROLES


# REGISTER
def register_user(data):
    existing = users_collection.find_one({"email": data.email})

    if existing:
        return {"error": "User already exists"}

    hashed_pw = hash_password(data.password)

    user = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pw,
        "role": "admin"
    }

    users_collection.insert_one(user)

    return {"message": "User registered successfully"}


# LOGIN
def login_user(data):
    user = users_collection.find_one({"email": data.email})

    if not user:
        return {"error": "User not found"}

    if not verify_password(data.password, user["password"]):
        return {"error": "Invalid password"}

    # Section 6 of the design doc: JWT payload must carry role + company_id
    # so every future request can be checked without hitting the DB again.
    token = create_token({
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
        "company_id": user.get("company_id"),
    })

    return {
        "token": token,
        "user": user["email"],
        "role": user["role"],
        "name": user["name"],
        "company_id": user.get("company_id"),
    }


# =====================================================
# SUPER ADMIN
# =====================================================

def create_super_admin_bootstrap(data):
    """
    Creates the FIRST Super Admin in the system.
    Guard rails:
      1. Caller must know the secret setup_key (from .env).
      2. Only works if zero Super Admins currently exist.
         (Prevents anyone from spamming new Super Admins later
         just because they still know the setup key.)
    """
    if data.setup_key != SUPER_ADMIN_SETUP_KEY:
        return {"error": "Invalid setup key"}

    already_exists = users_collection.find_one({"role": SUPER_ADMIN})
    if already_exists:
        return {"error": "A Super Admin already exists. Bootstrap is disabled."}

    existing_email = users_collection.find_one({"email": data.email})
    if existing_email:
        return {"error": "User already exists"}

    hashed_pw = hash_password(data.password)

    user = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pw,
        "role": SUPER_ADMIN,
        "company_id": None,  # Section 4: Null for Super Admin
    }

    users_collection.insert_one(user)

    return {"message": "Super Admin created successfully"}


def create_user_by_admin(data):
    """
    Lets an EXISTING Super Admin create any account:
    another Super Admin, a Company Admin, HR, or Employee.

    company_id is now OPTIONAL for every role. If it's left blank for a
    Company Admin/HR/Employee, they'll be created with company_id = None,
    and will need to be assigned to a company later (e.g. via a separate
    "assign to company" endpoint or during company onboarding).
    """
    if data.role not in ALL_ROLES:
        return {"error": f"Invalid role. Must be one of {ALL_ROLES}"}

    existing_email = users_collection.find_one({"email": data.email})
    if existing_email:
        return {"error": "User already exists"}

    hashed_pw = hash_password(data.password)

    user = {
        "name": data.name,
        "email": data.email,
        "password": hashed_pw,
        "role": data.role,
        "company_id": None if data.role == SUPER_ADMIN else data.company_id,
    }

    users_collection.insert_one(user)

    return {"message": f"{data.role} user created successfully"}


# from app.db.database import users_collection

# def register_user(data):
#     users_collection.insert_one(data)
#     return {"message": "User registered"}

from app.db.database import db
from app.core.hash import verify_password
from app.core.security import create_access_token

vendor_collection = db["vendors"]


def vendor_login(email: str, password: str):
    vendor = vendor_collection.find_one({
        "contact_details.email": email
    })

    # ❌ email not found
    if not vendor:
        return {"error": "Invalid email or password"}

    # ❌ not approved (IMPORTANT as per your workflow)
    if vendor["status"] != "APPROVED":
        return {"error": "Vendor not approved by admin"}

    # ❌ wrong password
    if not verify_password(password, vendor["password"]):
        return {"error": "Invalid email or password"}

    # ✅ create token
    token = create_access_token({
        "vendor_id": vendor["vendor_id"],
        "role": "vendor"
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "vendor_id": vendor["vendor_id"]
    }