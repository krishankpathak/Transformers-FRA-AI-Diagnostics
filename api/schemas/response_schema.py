from pydantic import BaseModel
from typing import List


class PredictionResponse(BaseModel):
    FRA_Result: str
    FDD_Result: int
    Final_Diagnosis: str
    Explanation: List[str]   # 🔥 ADD THIS