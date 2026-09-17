from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...models.post import Post
from ...schemas.post import PostResponse, PostUpdate, PostCreate

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("", response_model=List[PostResponse])
def list_posts(
    project_id: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    if project_id:
        query = query.filter(Post.project_id == project_id)
    if platform:
        query = query.filter(Post.platform == platform)
    if status:
        query = query.filter(Post.status == status)
    
    return query.order_by(Post.scheduled_time.asc()).limit(limit).all()

@router.post("", response_model=PostResponse)
def create_manual_post(post_in: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        project_id=post_in.project_id,
        campaign_id=post_in.campaign_id,
        platform=post_in.platform,
        day_number=post_in.day_number,
        topic=post_in.topic,
        hook=post_in.hook or "",
        content=post_in.content,
        scheduled_time=post_in.scheduled_time,
        status=post_in.status or "scheduled",
        auto_publish=post_in.auto_publish
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: str, update_in: PostUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if update_in.content is not None:
        post.content = update_in.content
    if update_in.topic is not None:
        post.topic = update_in.topic
    if update_in.scheduled_time is not None:
        post.scheduled_time = update_in.scheduled_time
    if update_in.status is not None:
        post.status = update_in.status
    if update_in.auto_publish is not None:
        post.auto_publish = update_in.auto_publish

    db.commit()
    db.refresh(post)
    return post

@router.post("/{post_id}/publish-now", response_model=PostResponse)
def publish_now(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "published"
    post.published_time = datetime.utcnow()
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(post_id: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"status": "deleted", "id": post_id}
