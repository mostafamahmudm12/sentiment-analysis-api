from pydantic import BaseModel
from typing import List, Union


class TrainingData(BaseModel):
    texts: List[str]
    labels: List[Union[str, int]]

class TestingData(BaseModel):
    texts: List[str]

class QueryText(BaseModel):
    text: str

