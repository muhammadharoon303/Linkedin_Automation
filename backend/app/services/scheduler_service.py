import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..core.database import SessionLocal
from ..models.post import Post
from ..models.account import SocialAccount
from ..models.system_setting import SystemSetting
from ..models.post_log import PostLog
from .publishers.registry import publisher_registry

logger = logging.getLogger("scheduler")
scheduler = AsyncIOScheduler()

async def check_and_publish_due_posts():
    """
    Main automated posting queue runner:
    1. Checks if Master Auto-Posting switch is ON.
    2. Queries all due posts in SQLite (scheduled_time <= now).
    3. Invokes the appropriate official platform adapter.
    4. Handles retries up to 3 times before setting status to 'failed'.
    5. Writes detailed audit logs to PostLog.
    """
    db = SessionLocal()
    try:
        # Check Master Auto-Posting switch
        setting = db.query(SystemSetting).filter(SystemSetting.key == "master_auto_posting").first()
        if setting and setting.value.lower() == "false":
            logger.info("Scheduler check: Master auto-posting switch is OFF. Skipping queue execution.")
            return

        now = datetime.utcnow()
        due_posts = db.query(Post).filter(
            Post.status == "scheduled",
            Post.auto_publish == True,
            Post.scheduled_time <= now
        ).all()

        if not due_posts:
            return

        logger.info(f"Processing {len(due_posts)} due posts...")

        for post in due_posts:
            # Find active social account for this platform
            account = db.query(SocialAccount).filter(
                SocialAccount.platform == post.platform,
                SocialAccount.is_active == True
            ).first()

            adapter = publisher_registry.get_adapter(post.platform)
            if not adapter:
                post.status = "failed"
                post.error_message = f"No adapter registered for platform: {post.platform}"
                db.add(post)
                db.add(PostLog(
                    post_id=post.id,
                    platform=post.platform,
                    action="publish",
                    status="error",
                    details=post.error_message
                ))
                continue

            # Attempt official publishing
            result = await adapter.publish(post, account)

            if result.success:
                post.status = "published"
                post.published_time = datetime.utcnow()
                post.error_message = None
                db.add(post)
                db.add(PostLog(
                    post_id=post.id,
                    platform=post.platform,
                    action="publish",
                    status="success",
                    details=result.details or f"Published with ID {result.platform_post_id}"
                ))
                logger.info(f"Post {post.id} successfully published to {post.platform}")
            else:
                post.retry_count = (post.retry_count or 0) + 1
                post.error_message = result.error

                if post.retry_count >= 3:
                    post.status = "failed"
                    action_name = "failed_permanently"
                else:
                    action_name = f"retry_attempt_{post.retry_count}"

                db.add(post)
                db.add(PostLog(
                    post_id=post.id,
                    platform=post.platform,
                    action=action_name,
                    status="error",
                    details=result.error or "Unknown error"
                ))
                logger.warning(f"Post {post.id} publish attempt failed: {result.error}")

        db.commit()

    except Exception as e:
        logger.error(f"Scheduler execution error: {e}")
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(check_and_publish_due_posts, "interval", seconds=30, id="due_posts_checker")
        scheduler.start()
        logger.info("Background posting scheduler started (30s interval).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background posting scheduler stopped.")
