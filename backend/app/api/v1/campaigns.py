import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...models.campaign import Campaign
from ...models.post import Post
from ...schemas.campaign import CampaignCreate, CampaignResponse
from ...schemas.post import PostResponse, DailyContentGenerationRequest, DualPlatformGenerationResponse
from ...services.campaign_service import campaign_service

router = APIRouter(tags=["Campaigns"])

@router.post("/projects/{project_id}/campaigns", response_model=CampaignResponse)
async def create_campaign(
    project_id: str,
    campaign_in: CampaignCreate,
    db: Session = Depends(get_db)
):
    try:
        campaign = await campaign_service.create_campaign(db, project_id, campaign_in)
        total_posts = db.query(Post).filter(Post.campaign_id == campaign.id).count()
        return CampaignResponse(
            id=campaign.id,
            project_id=campaign.project_id,
            title=campaign.title,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            platforms=json.loads(campaign.platforms_json),
            posting_hours=json.loads(campaign.posting_hours_json),
            auto_posting=campaign.auto_posting,
            status=campaign.status,
            created_at=campaign.created_at,
            total_posts=total_posts
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/projects/{project_id}/campaigns", response_model=List[CampaignResponse])
def list_project_campaigns(project_id: str, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter(Campaign.project_id == project_id).all()
    res = []
    for c in campaigns:
        total = db.query(Post).filter(Post.campaign_id == c.id).count()
        res.append(CampaignResponse(
            id=c.id,
            project_id=c.project_id,
            title=c.title,
            start_date=c.start_date,
            end_date=c.end_date,
            platforms=json.loads(c.platforms_json),
            posting_hours=json.loads(c.posting_hours_json),
            auto_posting=c.auto_posting,
            status=c.status,
            created_at=c.created_at,
            total_posts=total
        ))
    return res

@router.get("/campaigns/{campaign_id}/posts", response_model=List[PostResponse])
def get_campaign_posts(campaign_id: str, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.campaign_id == campaign_id).order_by(Post.scheduled_time.asc()).all()
    return posts

@router.post("/campaigns/daily-generate", response_model=DualPlatformGenerationResponse)
async def generate_daily_content(
    req: DailyContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generates both LinkedIn post and TikTok script from the same project data for a given day.
    """
    try:
        linkedin_p, tiktok_p = await campaign_service.generate_dual_platform_post(
            db=db,
            project_id=req.project_id,
            day_number=req.day_number,
            custom_topic=req.topic,
            campaign_id=req.campaign_id,
            scheduled_time=req.scheduled_time,
            model=req.model
        )
        return DualPlatformGenerationResponse(
            day_number=req.day_number,
            topic=linkedin_p.topic,
            linkedin_post=linkedin_p,
            tiktok_script=tiktok_p
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
