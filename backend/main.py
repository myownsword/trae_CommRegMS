from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import os

from database import engine, Base, get_db
from models import ActivityStatus, RegistrationStatus
from schemas import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityDetailResponse,
    RegistrationCreate,
    RegistrationCancel,
    RegistrationResponse,
    StatisticsResponse,
)
from crud import (
    get_activity,
    get_activities,
    get_activity_with_stats,
    create_activity,
    update_activity,
    cancel_activity,
    create_registration,
    get_active_registration_by_phone,
    get_registration_by_phone,
    cancel_registration,
    get_activity_registrations,
    count_active_registrations,
    get_statistics,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="社区活动报名管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _init_demo_data(db: Session):
    from models import Activity, Registration

    existing = db.query(Activity).count()
    if existing > 0:
        return

    now = datetime.utcnow()
    demo_activities = [
        Activity(
            title="社区乒乓球友谊赛",
            location="社区活动中心二楼 201室",
            start_time=now + timedelta(days=7, hours=3),
            max_participants=20,
            description="欢迎各位乒乓球爱好者参加本次友谊赛，比赛设冠亚季军及参与奖。请自带球拍。",
            status=ActivityStatus.OPEN,
        ),
        Activity(
            title="亲子烘焙工作坊",
            location="社区服务中心一楼厨房",
            start_time=now + timedelta(days=3, hours=9),
            max_participants=15,
            description="和孩子一起动手制作美味曲奇和小蛋糕，所有材料由活动方提供。建议6-12岁儿童参加，需家长陪同。",
            status=ActivityStatus.OPEN,
        ),
        Activity(
            title="老年人智能手机培训",
            location="社区图书馆",
            start_time=now + timedelta(days=10, hours=10),
            max_participants=25,
            description="帮助社区老年人掌握微信视频、线上挂号、健康码等常用功能。",
            status=ActivityStatus.OPEN,
        ),
        Activity(
            title="春季社区园艺讲座",
            location="社区花园凉亭",
            start_time=now + timedelta(days=2),
            max_participants=30,
            description="已圆满结束",
            status=ActivityStatus.CLOSED,
        ),
        Activity(
            title="夏日户外徒步活动",
            location="附近森林公园南门",
            start_time=now + timedelta(days=14, hours=6),
            max_participants=40,
            description="因天气原因取消",
            status=ActivityStatus.CANCELLED,
        ),
    ]

    for a in demo_activities:
        db.add(a)
    db.commit()

    for a in demo_activities:
        db.refresh(a)

    demo_registrations = [
        (demo_activities[0].id, "张三", "13800138001", "横拍选手"),
        (demo_activities[0].id, "李四", "13800138002", "直拍选手"),
        (demo_activities[0].id, "王五", "13800138003", None),
        (demo_activities[1].id, "赵晓丽", "13800138004", "带7岁女儿参加"),
        (demo_activities[1].id, "陈浩", "13800138005", "带8岁儿子参加"),
        (demo_activities[2].id, "周大爷", "13800138006", "想学微信视频"),
        (demo_activities[3].id, "孙七", "13800138007", None),
    ]

    for aid, name, phone, remark in demo_registrations:
        db.add(Registration(activity_id=aid, name=name, phone=phone, remark=remark))
    db.commit()


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    try:
        _init_demo_data(db)
    finally:
        db.close()


def _build_activity_response(db: Session, activity) -> ActivityResponse:
    current = count_active_registrations(db, activity.id)
    return ActivityResponse(
        id=activity.id,
        title=activity.title,
        location=activity.location,
        start_time=activity.start_time,
        max_participants=activity.max_participants,
        description=activity.description,
        status=activity.status,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
        current_participants=current,
        remaining_slots=max(0, activity.max_participants - current),
    )


@app.get("/")
def root():
    return {"message": "社区活动报名管理系统 API", "docs": "/docs"}


@app.get("/api/activities", response_model=List[ActivityResponse])
def list_activities(status: Optional[ActivityStatus] = None, db: Session = Depends(get_db)):
    activities = get_activities(db, status=status)
    return [_build_activity_response(db, a) for a in activities]


@app.get("/api/activities/{activity_id}", response_model=ActivityDetailResponse)
def get_activity_detail(activity_id: int, db: Session = Depends(get_db)):
    activity = get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    current = count_active_registrations(db, activity_id)
    registrations = get_activity_registrations(db, activity_id)
    reg_responses = [RegistrationResponse.model_validate(r) for r in registrations]
    return ActivityDetailResponse(
        id=activity.id,
        title=activity.title,
        location=activity.location,
        start_time=activity.start_time,
        max_participants=activity.max_participants,
        description=activity.description,
        status=activity.status,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
        current_participants=current,
        remaining_slots=max(0, activity.max_participants - current),
        registrations=reg_responses,
    )


@app.post("/api/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_new_activity(activity_in: ActivityCreate, db: Session = Depends(get_db)):
    activity = create_activity(db, activity_in)
    return _build_activity_response(db, activity)


@app.put("/api/activities/{activity_id}", response_model=ActivityResponse)
def update_existing_activity(
    activity_id: int, activity_in: ActivityUpdate, db: Session = Depends(get_db)
):
    activity = get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity_in.max_participants is not None:
        current = count_active_registrations(db, activity_id)
        if activity_in.max_participants < current:
            raise HTTPException(
                status_code=400,
                detail=f"人数上限不能低于当前已报名人数({current})",
            )
    updated = update_activity(db, activity, activity_in)
    return _build_activity_response(db, updated)


@app.post("/api/activities/{activity_id}/cancel", response_model=ActivityResponse)
def cancel_existing_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity.status == ActivityStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="活动已取消，无需重复操作")
    cancelled = cancel_activity(db, activity)
    return _build_activity_response(db, cancelled)


@app.post(
    "/api/activities/{activity_id}/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_for_activity(
    activity_id: int, reg_in: RegistrationCreate, db: Session = Depends(get_db)
):
    activity = get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    if activity.status == ActivityStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="活动已取消，无法报名")
    if activity.status == ActivityStatus.CLOSED:
        raise HTTPException(status_code=400, detail="活动已结束，无法报名")
    if activity.status == ActivityStatus.DRAFT:
        raise HTTPException(status_code=400, detail="活动尚未开放报名")

    existing = get_active_registration_by_phone(db, activity_id, reg_in.phone)
    if existing:
        raise HTTPException(status_code=409, detail="该手机号已报名此活动，不能重复报名")

    current = count_active_registrations(db, activity_id)
    if current >= activity.max_participants:
        raise HTTPException(status_code=400, detail="活动名额已满，报名失败")

    registration = create_registration(db, activity_id, reg_in)
    return RegistrationResponse.model_validate(registration)


@app.post("/api/activities/{activity_id}/registrations/cancel", response_model=RegistrationResponse)
def cancel_user_registration(
    activity_id: int, cancel_in: RegistrationCancel, db: Session = Depends(get_db)
):
    activity = get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    reg = get_active_registration_by_phone(db, activity_id, cancel_in.phone)
    if not reg:
        existing_cancelled = get_registration_by_phone(db, activity_id, cancel_in.phone)
        if existing_cancelled:
            raise HTTPException(status_code=400, detail="该手机号的报名已取消")
        raise HTTPException(status_code=404, detail="未找到该手机号的报名记录")
    cancelled = cancel_registration(db, reg)
    return RegistrationResponse.model_validate(cancelled)


@app.get("/api/statistics", response_model=StatisticsResponse)
def get_system_statistics(db: Session = Depends(get_db)):
    return get_statistics(db)
