from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict, Any
from ...core.database import get_db
from ...models.post import Post
from ...models.post_log import PostLog
from ...models.system_setting import SystemSetting

router = APIRouter(prefix="/analytics", tags=["Analytics & System Controls"])

class MasterSwitchUpdate(BaseModel):
    enabled: bool

class LogResponse(BaseModel):
    id: str
    post_id: str
    platform: str
    action: str
    status: str
    details: str
    created_at: str

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_posts = db.query(Post).count()
    published = db.query(Post).filter(Post.status == "published").count()
    scheduled = db.query(Post).filter(Post.status == "scheduled").count()
    failed = db.query(Post).filter(Post.status == "failed").count()
    drafts = db.query(Post).filter(Post.status == "draft").count()

    # Platform breakdown
    platform_counts = db.query(
        Post.platform, func.count(Post.id)
    ).group_by(Post.platform).all()

    # Success rate
    completed = published + failed
    success_rate = round((published / completed * 100), 1) if completed > 0 else 100.0

    return {
        "total_posts": total_posts,
        "published_count": published,
        "scheduled_count": scheduled,
        "failed_count": failed,
        "draft_count": drafts,
        "success_rate_percent": success_rate,
        "platforms": {p: count for p, count in platform_counts}
    }

@router.get("/master-switch")
def get_master_switch(db: Session = Depends(get_db)) -> Dict[str, Any]:
    setting = db.query(SystemSetting).filter(SystemSetting.key == "master_auto_posting").first()
    enabled = True
    if setting and setting.value.lower() == "false":
        enabled = False
    return {"master_auto_posting": enabled}

@router.post("/master-switch")
def update_master_switch(req: MasterSwitchUpdate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    setting = db.query(SystemSetting).filter(SystemSetting.key == "master_auto_posting").first()
    str_val = "true" if req.enabled else "false"
    if setting:
        setting.value = str_val
    else:
        setting = SystemSetting(key="master_auto_posting", value=str_val)
        db.add(setting)
    db.commit()
    return {"master_auto_posting": req.enabled, "status": "updated"}

@router.get("/logs", response_model=List[LogResponse])
def get_system_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(PostLog).order_by(PostLog.created_at.desc()).limit(limit).all()
    return [
        LogResponse(
            id=log.id,
            post_id=log.post_id,
            platform=log.platform,
            action=log.action,
            status=log.status,
            details=log.details or "",
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]
