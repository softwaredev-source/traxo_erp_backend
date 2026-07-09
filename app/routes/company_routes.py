from app.utils.dependencies import get_current_user
from app.utils.role_checker import require_super_admin
from fastapi import APIRouter, HTTPException,Depends
from app.schemas.company_schema import CompanySchema
from app.controllers.company_controller import create_company_controller, get_companies_controller

router = APIRouter(prefix="/company", tags=["Company"])

@router.post("/onboard")
def onboard_company(data: CompanySchema, current_user=Depends(require_super_admin)):
    try:
        result = create_company_controller(data)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.get("/get-companies")
def get_companies(current_user=Depends(require_super_admin)):
    try:
        return get_companies_controller()
    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")    