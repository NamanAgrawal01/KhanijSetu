"""
KhanijSetu Notifications API — user notifications.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, Notification
from app.auth.jwt_handler import get_current_user
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def get_notifications(
    status: Optional[str] = None,
    skip: int = 0, limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notifications for current user."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if status:
        query = query.filter(Notification.status == status)

    total = query.count()
    unread = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.status == "unread"
    ).count()
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "notifications": [{
            "id": n.id, "title": n.title, "message": n.message,
            "type": n.type, "severity": n.severity,
            "link": n.link, "status": n.status,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        } for n in notifications],
        "total": total,
        "unread": unread,
    }


@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get unread notification count."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.status == "unread"
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.status = "read"
    db.commit()
    return {"status": "success"}


@router.put("/read-all")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.status == "unread"
    ).update({"status": "read"})
    db.commit()
    return {"status": "success"}
