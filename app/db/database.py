from pymongo import MongoClient
from app.core.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
print("MongoDB Connected Successfully")

users_collection = db["adminUsers"]
company_collection = db["companies"]
vendor_collection = db["vendors"]
procurement_collection = db["procurement"]
requirement_collection = db["requirements"]
product_collection = db["products"]
depertment_Head_collection = db["department_head"]
modules_collection = db["modules"]
department_employees_collection = db["department_employees"]
payroll_policy_collection = db["payroll_policy"]
company_leave_types_collection = db["company_leave_types"]
counters_collection = db["counters"]