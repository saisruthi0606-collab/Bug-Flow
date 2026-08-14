from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.notification import Notification
from ...models.user import User
from ...utils.auth import get_current_user
router=APIRouter()
@router.get('')
def list_notifications(limit:int=30,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    rows=db.query(Notification).filter(Notification.user_id==current_user.id).order_by(Notification.created_at.desc()).limit(min(limit,100)).all()
    return {"unread_count":db.query(Notification).filter(Notification.user_id==current_user.id,Notification.is_read.is_(False)).count(),"items":rows}
@router.put('/{notification_id}/read')
def mark_read(notification_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    item=db.query(Notification).filter(Notification.id==notification_id,Notification.user_id==current_user.id).first()
    if not item:
        raise HTTPException(status_code=404,detail='Notification not found')
    item.is_read=True
    db.commit()
    return {"message":"Notification marked read"}

@router.delete('/{notification_id}')
def delete_notification(notification_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    item=db.query(Notification).filter(Notification.id==notification_id,Notification.user_id==current_user.id).first()
    if not item:
        raise HTTPException(status_code=404,detail='Notification not found')
    db.delete(item)
    db.commit()
    return {"message":"Notification deleted"}

@router.put('/read-all')
def read_all(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id==current_user.id,Notification.is_read.is_(False)).update({Notification.is_read:True})
    db.commit()
    return {"message":"Notifications marked read"}
