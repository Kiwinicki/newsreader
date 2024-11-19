from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class User(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True, extra="ignore")

class News(BaseModel):
    uuid: str
    title: str
    description: str
    keywords: str
    snippet: str
    url: str
    image_url: str
    language: str
    published_at: datetime
    source: str
    categories: List[str]
    relevance_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")