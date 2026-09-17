import os
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...models.account import SocialAccount
from ...services.publishers.linkedin import linkedin_adapter

router = APIRouter(prefix="/oauth", tags=["OAuth & Accounts"])

class AccountResponse(BaseModel):
    id: str
    platform: str
    account_name: str
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ManualTokenConnect(BaseModel):
    platform: str
    account_name: str
    access_token: str
    account_urn: Optional[str] = None
    expires_in_days: int = 60

@router.get("/accounts", response_model=List[AccountResponse])
def list_connected_accounts(db: Session = Depends(get_db)):
    """Lists all connected social accounts without exposing secrets."""
    return db.query(SocialAccount).all()

@router.delete("/accounts/{account_id}")
def disconnect_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(SocialAccount).filter(SocialAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"status": "disconnected", "id": account_id}

@router.get("/linkedin/authorize-url")
def get_linkedin_authorize_url(
    client_id: Optional[str] = Query(None),
    redirect_uri: Optional[str] = Query(None)
):
    """
    Returns the official LinkedIn OAuth 2.0 Authorization URL.
    Uses LINKEDIN_CLIENT_ID and LINKEDIN_REDIRECT_URI from backend environment if not passed.
    """
    effective_client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID", "")
    effective_redirect_uri = redirect_uri or os.getenv(
        "LINKEDIN_REDIRECT_URI",
        "http://localhost:8000/api/v1/oauth/linkedin/callback"
    )

    if not effective_client_id:
        raise HTTPException(
            status_code=400,
            detail="LINKEDIN_CLIENT_ID is not configured in backend .env file."
        )

    state = str(uuid.uuid4())
    url = linkedin_adapter.get_authorization_url(
        client_id=effective_client_id,
        redirect_uri=effective_redirect_uri,
        state=state
    )
    return {"authorize_url": url, "state": state}

@router.get("/linkedin/callback")
async def linkedin_oauth_callback(
    code: str = Query(..., description="Authorization code returned by LinkedIn"),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    LinkedIn OAuth redirect callback.
    Securely exchanges code for access token on the backend and saves it in SQLite.
    """
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = os.getenv(
        "LINKEDIN_REDIRECT_URI",
        "http://localhost:8000/api/v1/oauth/linkedin/callback"
    )

    if not client_id or not client_secret:
        return HTMLResponse(
            "<h2>Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in backend .env</h2>",
            status_code=500
        )

    try:
        token_data = await linkedin_adapter.exchange_code_for_token(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri
        )

        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 5184000) # 60 days standard
        refresh_token = token_data.get("refresh_token")

        name = "Muhammad Haroon"
        author_urn = None
        try:
            profile = await linkedin_adapter.get_user_profile(access_token)
            sub_id = profile.get("sub", "")
            name = profile.get("name", name)
            author_urn = f"urn:li:person:{sub_id}" if sub_id else None
        except Exception:
            pass

        # Update primary LinkedIn account or create if none exists
        existing = db.query(SocialAccount).filter(
            SocialAccount.platform == "linkedin"
        ).order_by(SocialAccount.created_at.desc()).first()

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        if existing:
            existing.account_name = name
            existing.account_urn = author_urn or existing.account_urn
            existing.access_token = access_token
            existing.refresh_token = refresh_token
            existing.expires_at = expires_at
            existing.is_active = True
        else:
            new_acc = SocialAccount(
                platform="linkedin",
                account_name=name,
                account_urn=author_urn,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                is_active=True
            )
            db.add(new_acc)

        # Deactivate any duplicate old accounts
        db.commit()
        if existing:
            db.query(SocialAccount).filter(
                SocialAccount.platform == "linkedin",
                SocialAccount.id != existing.id
            ).delete()
            db.commit()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkedIn Connected</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 50px; background: #f8fafc; }}
                .card {{ background: white; max-width: 450px; margin: 0 auto; padding: 30px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
                h2 {{ color: #0A66C2; }}
                p {{ color: #475569; font-size: 15px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>✓ LinkedIn Connected Successfully!</h2>
                <p>Authenticated as <b>{name}</b>.</p>
                <p>Your access token is securely stored on your local backend. You can now close this tab and return to the Flutter app.</p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(
            f"<h2>LinkedIn Authentication Failed</h2><p>{str(e)}</p>",
            status_code=400
        )

@router.post("/connect-manual", response_model=AccountResponse)
def connect_manual_token(req: ManualTokenConnect, db: Session = Depends(get_db)):
    """
    Connects a token directly (useful for local development or sandbox testing).
    """
    expires_at = datetime.utcnow() + timedelta(days=req.expires_in_days)
    acc = SocialAccount(
        platform=req.platform.lower(),
        account_name=req.account_name,
        account_urn=req.account_urn,
        access_token=req.access_token,
        expires_at=expires_at,
        is_active=True
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc
