from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

from models import ActivityStatus, RegistrationStatus


class RegistrationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class RegistrationCreate(RegistrationBase):
    pass


class RegistrationCancel(BaseModel):
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class RegistrationResponse(BaseModel):
    id: int
    activity_id: int
    name: str
    phone: str
    remark: Optional[str]
    status: RegistrationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="活动标题")
    location: str = Field(..., min_length=1, max_length=300, description="活动地点")
    start_time: datetime = Field(..., description="开始时间")
    max_participants: int = Field(..., ge=1, description="人数上限")
    description: Optional[str] = Field(None, description="活动说明")
    status: ActivityStatus = Field(default=ActivityStatus.OPEN, description="活动状态")


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, min_length=1, max_length=300)
    start_time: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    status: Optional[ActivityStatus] = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    location: str
    start_time: datetime
    max_participants: int
    description: Optional[str]
    status: ActivityStatus
    created_at: datetime
    updated_at: datetime
    current_participants: int = 0
    remaining_slots: int = 0

    class Config:
        from_attributes = True


class ActivityDetailResponse(ActivityResponse):
    registrations: List[RegistrationResponse] = []


class StatisticsResponse(BaseModel):
    total_activities: int
    open_activities: int
    total_registrations: int


class ErrorResponse(BaseModel):
    detail: str
