from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

from models import Activity, Registration, ActivityStatus, RegistrationStatus
from schemas import ActivityCreate, ActivityUpdate, RegistrationCreate


def get_activity(db: Session, activity_id: int) -> Optional[Activity]:
    return db.query(Activity).filter(Activity.id == activity_id).first()


def get_activities(db: Session, status: Optional[ActivityStatus] = None) -> List[Activity]:
    query = db.query(Activity)
    if status:
        query = query.filter(Activity.status == status)
    return query.order_by(Activity.created_at.desc()).all()


def count_active_registrations(db: Session, activity_id: int) -> int:
    return (
        db.query(func.count(Registration.id))
        .filter(
            Registration.activity_id == activity_id,
            Registration.status == RegistrationStatus.ACTIVE,
        )
        .scalar()
        or 0
    )


def get_activity_with_stats(db: Session, activity: Activity):
    current = count_active_registrations(db, activity.id)
    activity.current_participants = current
    activity.remaining_slots = max(0, activity.max_participants - current)
    return activity


def create_activity(db: Session, activity_in: ActivityCreate) -> Activity:
    db_activity = Activity(
        title=activity_in.title,
        location=activity_in.location,
        start_time=activity_in.start_time,
        max_participants=activity_in.max_participants,
        description=activity_in.description,
        status=activity_in.status,
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(db: Session, db_activity: Activity, activity_in: ActivityUpdate) -> Activity:
    update_data = activity_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_activity, field, value)
    db_activity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_activity)
    return db_activity


def cancel_activity(db: Session, db_activity: Activity) -> Activity:
    db_activity.status = ActivityStatus.CANCELLED
    db_activity.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_activity)
    return db_activity


def create_registration(db: Session, activity_id: int, reg_in: RegistrationCreate) -> Registration:
    db_reg = Registration(
        activity_id=activity_id,
        name=reg_in.name,
        phone=reg_in.phone,
        remark=reg_in.remark,
    )
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)
    return db_reg


def get_registration_by_phone(db: Session, activity_id: int, phone: str) -> Optional[Registration]:
    return (
        db.query(Registration)
        .filter(
            Registration.activity_id == activity_id,
            Registration.phone == phone,
        )
        .first()
    )


def get_active_registration_by_phone(db: Session, activity_id: int, phone: str) -> Optional[Registration]:
    return (
        db.query(Registration)
        .filter(
            Registration.activity_id == activity_id,
            Registration.phone == phone,
            Registration.status == RegistrationStatus.ACTIVE,
        )
        .first()
    )


def cancel_registration(db: Session, db_reg: Registration) -> Registration:
    db_reg.status = RegistrationStatus.CANCELLED
    db_reg.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_reg)
    return db_reg


def get_activity_registrations(db: Session, activity_id: int) -> List[Registration]:
    return (
        db.query(Registration)
        .filter(Registration.activity_id == activity_id)
        .order_by(Registration.created_at.desc())
        .all()
    )


def get_statistics(db: Session):
    total_activities = db.query(func.count(Activity.id)).scalar() or 0
    open_activities = (
        db.query(func.count(Activity.id))
        .filter(Activity.status == ActivityStatus.OPEN)
        .scalar()
        or 0
    )
    total_registrations = (
        db.query(func.count(Registration.id))
        .filter(Registration.status == RegistrationStatus.ACTIVE)
        .scalar()
        or 0
    )
    return {
        "total_activities": total_activities,
        "open_activities": open_activities,
        "total_registrations": total_registrations,
    }
