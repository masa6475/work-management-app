from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class WorkRecordBase(BaseModel):
    record_date: datetime
    customer_name: str = Field(..., min_length=1, max_length=200)
    work_content: str = Field(..., min_length=1)
    work_type: str = Field(default="一般", max_length=100)
    status: str = Field(default="未対応", max_length=50)
    duration_minutes: int = Field(default=0, ge=0)
    note: str = ""


class WorkRecordCreate(WorkRecordBase):
    pass


class WorkRecordResponse(WorkRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
