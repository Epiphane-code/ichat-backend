from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_status():
    return {"message": "Liste des status"}