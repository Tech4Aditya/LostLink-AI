from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: str
    model_config = {"from_attributes": True}

class ReportOut(BaseModel):
    id: UUID
    type: str
    category: str
    description: str
    color: str | None
    location_name: str
    latitude: float | None
    longitude: float | None
    event_time: datetime | None
    status: str
    image_url: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}

class MatchOut(BaseModel):
    id: UUID
    lost_report_id: UUID
    found_report_id: UUID
    visual_score: float
    text_score: float
    attribute_score: float
    location_score: float
    time_score: float
    final_score: float
    status: str
    explanation: dict
    created_at: datetime
    model_config = {"from_attributes": True}

class ClaimCreate(BaseModel):
    private_detail: str = Field(min_length=1, max_length=2000)

class ClaimOut(BaseModel):
    id: UUID
    match_id: UUID
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
