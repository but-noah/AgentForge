"""Vector Store service for Qdrant integration."""

import os
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
from openai import AsyncOpenAI

from app.models import DistanceMetric


class VectorStore:
    """Service for managing vector embeddings and semantic search with Qdrant."""

    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key if self.qdrant_api_key else None,
        )
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_distance(self, metric: DistanceMetric) -> Distance:
        """Convert DistanceMetric enum to Qdrant Distance."""
        mapping = {
            DistanceMetric.COSINE: Distance.COSINE,
            DistanceMetric.EUCLIDEAN: Distance.EUCLID,
            DistanceMetric.DOT_PRODUCT: Distance.DOT,
        }
        return mapping.get(metric, Distance.COSINE)

    async def create_collection(
        self,
        collection_name: str,
        dimension: int = 1536,
        distance_metric: DistanceMetric = DistanceMetric.COSINE,
    ) -> bool:
        """Create a new vector collection in Qdrant."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=self._get_distance(distance_metric)
                ),
            )
            return True
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False

    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = await self.openai_client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    async def embed_document(
        self,
        collection_name: str,
        document_id: UUID,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Embed a document and store it in Qdrant."""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(text)

            # Create point ID
            point_id = str(uuid4())

            # Prepare payload
            payload = {
                "document_id": str(document_id),
                "text": text,
                "metadata": metadata or {},
            }

            # Upsert point
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )

            return point_id
        except Exception as e:
            print(f"Error embedding document: {e}")
            raise

    async def semantic_search(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on a collection."""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Prepare filter if provided
            search_filter = None
            if filter_conditions:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )

            # Perform search
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=search_filter,
            )

            # Format results
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "document_id": result.payload.get("document_id"),
                    "text": result.payload.get("text"),
                    "metadata": result.payload.get("metadata", {}),
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error performing semantic search: {e}")
            raise

    async def delete_document(
        self,
        collection_name: str,
        point_id: str,
    ) -> bool:
        """Delete a document from the collection."""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=[point_id],
            )
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire collection."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except Exception as e:
            print(f"Error checking collection existence: {e}")
            return False
