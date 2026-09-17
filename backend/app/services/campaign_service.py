import json
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.project import Project
from ..models.campaign import Campaign
from ..models.post import Post
from ..models.document import Document
from ..schemas.campaign import CampaignCreate
from .ollama_service import ollama_service

class CampaignService:
    @staticmethod
    async def create_campaign(
        db: Session,
        project_id: str,
        campaign_in: CampaignCreate
    ) -> Campaign:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Save campaign record
        campaign = Campaign(
            project_id=project_id,
            title=campaign_in.title,
            start_date=campaign_in.start_date,
            end_date=campaign_in.end_date,
            platforms_json=json.dumps(campaign_in.platforms),
            posting_hours_json=json.dumps(campaign_in.posting_hours),
            auto_posting=campaign_in.auto_posting,
            status="active"
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        # Retrieve documents to extract topics and reference material
        docs = db.query(Document).filter(Document.project_id == project_id).all()
        ref_context = "\n---\n".join([f"Document '{d.title}':\n{d.raw_content}" for d in docs])
        
        # Collect extracted content plans if available
        plan_angles: List[str] = []
        for d in docs:
            try:
                angles = json.loads(d.content_plan_json)
                if isinstance(angles, list):
                    plan_angles.extend(angles)
            except Exception:
                pass

        # Calculate number of days
        delta_days = (campaign_in.end_date.date() - campaign_in.start_date.date()).days + 1
        delta_days = max(1, min(delta_days, 60))

        previous_topics: List[str] = []

        # Generate posts for each day and each platform
        for day_idx in range(delta_days):
            day_number = day_idx + 1
            current_date = campaign_in.start_date + timedelta(days=day_idx)

            # Pick topic from extracted plan or fallback rotation
            if day_idx < len(plan_angles):
                topic = plan_angles[day_idx]
            else:
                topic = f"{project.name} - Practical Insight Day {day_number}"

            previous_topics.append(topic)

            for platform in campaign_in.platforms:
                for hour in campaign_in.posting_hours:
                    scheduled_time = datetime(
                        current_date.year,
                        current_date.month,
                        current_date.day,
                        hour,
                        0
                    )

                    content = await ollama_service.generate_post(
                        platform=platform,
                        topic=topic,
                        reference_context=ref_context,
                        tone=project.tone_preference,
                        target_audience=project.target_audience,
                        previous_topics=previous_topics[:-1],
                        model=campaign_in.model
                    )

                    post = Post(
                        project_id=project_id,
                        campaign_id=campaign.id,
                        platform=platform,
                        day_number=day_number,
                        topic=topic,
                        hook=f"Day {day_number}: {topic}",
                        content=content,
                        status="scheduled",
                        scheduled_time=scheduled_time,
                        auto_publish=campaign_in.auto_posting
                    )
                    db.add(post)

        db.commit()
        db.refresh(campaign)
        return campaign

    @staticmethod
    async def generate_dual_platform_post(
        db: Session,
        project_id: str,
        day_number: int = 1,
        custom_topic: Optional[str] = None,
        campaign_id: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
        model: Optional[str] = None
    ) -> tuple[Post, Post]:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        docs = db.query(Document).filter(Document.project_id == project_id).all()
        ref_context = "\n---\n".join([f"{d.title}:\n{d.raw_content}" for d in docs])

        topic = custom_topic or f"{project.name} - Growth Framework"
        post_time = scheduled_time or (datetime.utcnow() + timedelta(hours=2))

        # Generate LinkedIn post
        linkedin_content = await ollama_service.generate_post(
            platform="linkedin",
            topic=topic,
            reference_context=ref_context,
            tone=project.tone_preference,
            target_audience=project.target_audience,
            model=model
        )

        linkedin_post = Post(
            project_id=project_id,
            campaign_id=campaign_id,
            platform="linkedin",
            day_number=day_number,
            topic=topic,
            hook=f"Day {day_number}: {topic}",
            content=linkedin_content,
            status="scheduled",
            scheduled_time=post_time,
            auto_publish=True
        )
        db.add(linkedin_post)

        # Generate TikTok script from the exact same project data
        tiktok_content = await ollama_service.generate_post(
            platform="tiktok",
            topic=topic,
            reference_context=ref_context,
            tone=project.tone_preference,
            target_audience=project.target_audience,
            model=model
        )

        tiktok_post = Post(
            project_id=project_id,
            campaign_id=campaign_id,
            platform="tiktok",
            day_number=day_number,
            topic=topic,
            hook=f"Day {day_number}: {topic}",
            content=tiktok_content,
            status="scheduled",
            scheduled_time=post_time + timedelta(hours=4),
            auto_publish=True
        )
        db.add(tiktok_post)

        db.commit()
        db.refresh(linkedin_post)
        db.refresh(tiktok_post)

        return linkedin_post, tiktok_post

campaign_service = CampaignService()
