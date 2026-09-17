import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...models.project import Project
from ...models.document import Document
from ...schemas.document import DocumentCreate, DocumentResponse
from ...services.ollama_service import ollama_service

router = APIRouter(tags=["Documents"])

@router.post("/projects/{project_id}/documents", response_model=DocumentResponse)
async def upload_and_analyze_document(
    project_id: str,
    doc_in: DocumentCreate,
    model: Optional[str] = Query(None, description="Ollama model to use"),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Analyze document with Ollama local AI
    analysis = await ollama_service.analyze_project_document(
        title=doc_in.title,
        content=doc_in.raw_content,
        model=model
    )

    document = Document(
        project_id=project_id,
        title=doc_in.title,
        raw_content=doc_in.raw_content,
        topics_json=json.dumps(analysis.get("topics", [])),
        benefits_json=json.dumps(analysis.get("benefits", [])),
        applications_json=json.dumps(analysis.get("applications", [])),
        technologies_json=json.dumps(analysis.get("technologies", [])),
        content_plan_json=json.dumps(analysis.get("thirty_day_content_plan", []))
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return DocumentResponse(
        id=document.id,
        project_id=document.project_id,
        title=document.title,
        raw_content=document.raw_content,
        topics=json.loads(document.topics_json),
        benefits=json.loads(document.benefits_json),
        applications=json.loads(document.applications_json),
        technologies=json.loads(document.technologies_json),
        content_plan=json.loads(document.content_plan_json),
        created_at=document.created_at
    )

@router.get("/projects/{project_id}/documents", response_model=List[DocumentResponse])
def list_project_documents(project_id: str, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.project_id == project_id).all()
    res = []
    for d in docs:
        res.append(DocumentResponse(
            id=d.id,
            project_id=d.project_id,
            title=d.title,
            raw_content=d.raw_content,
            topics=json.loads(d.topics_json) if d.topics_json else [],
            benefits=json.loads(d.benefits_json) if d.benefits_json else [],
            applications=json.loads(d.applications_json) if d.applications_json else [],
            technologies=json.loads(d.technologies_json) if d.technologies_json else [],
            content_plan=json.loads(d.content_plan_json) if d.content_plan_json else [],
            created_at=d.created_at
        ))
    return res

@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"status": "deleted", "id": document_id}
