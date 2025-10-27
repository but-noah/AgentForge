"""Vector and Document routes for AgentForge API."""

from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models import VectorCollection, Document
from app.schemas import (
    VectorCollectionCreate, VectorCollectionRead,
    DocumentCreate, DocumentRead,
    VectorSearchRequest, VectorSearchResponse, VectorSearchResult
)
from app.services import VectorStore
from app.users import current_active_user, User

router = APIRouter(prefix="/vectors", tags=["vectors"])


@router.post("/collections", response_model=VectorCollectionRead, status_code=status.HTTP_201_CREATED)
async def create_vector_collection(
    collection_data: VectorCollectionCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create a new vector collection."""
    # Generate unique collection name
    collection_name = f"collection_{uuid4().hex[:16]}"

    # Create in Qdrant
    vector_store = VectorStore()
    success = await vector_store.create_collection(
        collection_name=collection_name,
        dimension=collection_data.dimension,
        distance_metric=collection_data.distance_metric,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vector collection"
        )

    # Create in database
    collection = VectorCollection(
        **collection_data.model_dump(),
        qdrant_collection_name=collection_name,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return collection


@router.get("/collections/{collection_id}", response_model=VectorCollectionRead)
async def get_vector_collection(
    collection_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get a vector collection by ID."""
    result = await db.execute(
        select(VectorCollection).where(VectorCollection.id == collection_id)
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector collection not found"
        )

    return collection


@router.get("/collections", response_model=List[VectorCollectionRead])
async def list_vector_collections(
    workspace_id: UUID | None = None,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all vector collections."""
    query = select(VectorCollection)

    if workspace_id:
        query = query.where(VectorCollection.workspace_id == workspace_id)

    result = await db.execute(query)
    collections = result.scalars().all()

    return list(collections)


@router.post("/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Create a new document and embed it."""
    # Create document
    document = Document(**document_data.model_dump())
    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Embed if collection is specified
    if document.vector_collection_id:
        result = await db.execute(
            select(VectorCollection).where(
                VectorCollection.id == document.vector_collection_id
            )
        )
        collection = result.scalar_one_or_none()

        if collection:
            vector_store = VectorStore()
            try:
                point_id = await vector_store.embed_document(
                    collection_name=collection.qdrant_collection_name,
                    document_id=document.id,
                    text=document.content,
                    metadata=document.metadata,
                )
                document.embeddings_id = point_id
                await db.commit()
                await db.refresh(document)
            except Exception as e:
                print(f"Error embedding document: {e}")

    return document


@router.get("/documents/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Get a document by ID."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.get("/documents", response_model=List[DocumentRead])
async def list_documents(
    workspace_id: UUID | None = None,
    agent_id: UUID | None = None,
    collection_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """List all documents with optional filters."""
    query = select(Document)

    if workspace_id:
        query = query.where(Document.workspace_id == workspace_id)
    if agent_id:
        query = query.where(Document.agent_id == agent_id)
    if collection_id:
        query = query.where(Document.vector_collection_id == collection_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    documents = result.scalars().all()

    return list(documents)


@router.post("/search", response_model=VectorSearchResponse)
async def search_vectors(
    search_request: VectorSearchRequest,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Perform semantic search on a vector collection."""
    # Get collection
    result = await db.execute(
        select(VectorCollection).where(
            VectorCollection.id == search_request.collection_id
        )
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector collection not found"
        )

    # Perform search
    vector_store = VectorStore()
    try:
        results = await vector_store.semantic_search(
            collection_name=collection.qdrant_collection_name,
            query=search_request.query,
            limit=search_request.limit,
        )

        # Format results
        search_results = [
            VectorSearchResult(
                document_id=UUID(result["document_id"]),
                content=result["text"],
                score=result["score"],
                metadata=result["metadata"],
            )
            for result in results
        ]

        return VectorSearchResponse(results=search_results)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}"
        )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user),
):
    """Delete a document."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete from Qdrant if embedded
    if document.embeddings_id and document.vector_collection_id:
        result = await db.execute(
            select(VectorCollection).where(
                VectorCollection.id == document.vector_collection_id
            )
        )
        collection = result.scalar_one_or_none()

        if collection:
            vector_store = VectorStore()
            await vector_store.delete_document(
                collection_name=collection.qdrant_collection_name,
                point_id=document.embeddings_id,
            )

    await db.delete(document)
    await db.commit()
