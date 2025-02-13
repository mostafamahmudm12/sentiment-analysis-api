from pydantic import BaseModel
from typing import List, Dict

class StatusObject(BaseModel):
    status: str
    timestamp: str
    classes: List[str]
    evaluation: Dict
    
class PredictionObject(BaseModel):
    text: str
    predictions: Dict

class PredictionsObject(BaseModel):
    predictions: List[PredictionObject]
