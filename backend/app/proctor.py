from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/proctor", tags=["Proctor"])

class Terminate(BaseModel):
    exam_id: int
    reason: str
    violations: int

@router.post("/terminate")
def terminate_exam(data: Terminate):
    print("EXAM TERMINATED:", data.dict())
    return {"ok": True}
