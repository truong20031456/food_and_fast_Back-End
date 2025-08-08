"""
Elasticsearch Client - Analytics Service.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError

from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ElasticsearchClient:
    """Elasticsearch client for analytics data storage and retrieval."""

    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None
        self.is_connected = False

    async def connect(self):
        """Connect to Elasticsearch."""
        try:
            # Use the client configuration from settings
            client_config = settings.elasticsearch.client_config
            
            self.client = AsyncElasticsearch(**client_config)

            # Test connection
            await self.health_check()
            self.is_connected = True
            logger.info(f"Successfully connected to Elasticsearch at {settings.elasticsearch.host}:{settings.elasticsearch.port}")

        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            self.is_connected = False
            raise

    async def disconnect(self):
        """Disconnect from Elasticsearch."""
        if self.client:
            await self.client.close()
            self.is_connected = False
            logger.info("Disconnected from Elasticsearch")

    async def health_check(self) -> bool:
        """Check Elasticsearch health."""
        try:
            if not self.client:
                return False

            health = await self.client.cluster.health()
            return health.get("status") in ["green", "yellow"]

        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False

    async def create_index(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        """Create an index with mapping."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            # Check if index already exists
            if await self.client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            await self.client.indices.create(
                index=index_name,
                body={"mappings": mapping},
            )
            logger.info(f"Created index: {index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            return False

    async def index_document(
        self, index_name: str, document: Dict[str, Any], doc_id: Optional[str] = None
    ) -> bool:
        """Index a document."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            # Add timestamp if not present
            if "timestamp" not in document:
                document["timestamp"] = datetime.utcnow().isoformat()

            params = {"index": index_name, "body": document}
            if doc_id:
                params["id"] = doc_id

            result = await self.client.index(**params)
            logger.debug(f"Indexed document in {index_name}: {result['_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to index document in {index_name}: {e}")
            return False

    async def search(
        self,
        index_name: str,
        query: Dict[str, Any],
        size: int = 10,
        from_: int = 0,
        sort: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Search documents."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            search_body = {
                "query": query,
                "size": size,
                "from": from_,
            }

            if sort:
                search_body["sort"] = sort

            result = await self.client.search(index=index_name, body=search_body)
            return result

        except NotFoundError:
            logger.warning(f"Index {index_name} not found")
            return {"hits": {"hits": [], "total": {"value": 0}}}
        except Exception as e:
            logger.error(f"Failed to search in {index_name}: {e}")
            return {"hits": {"hits": [], "total": {"value": 0}}}

    async def aggregate(
        self, index_name: str, aggregations: Dict[str, Any], query: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform aggregations."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            search_body = {"aggs": aggregations, "size": 0}

            if query:
                search_body["query"] = query

            result = await self.client.search(index=index_name, body=search_body)
            return result.get("aggregations", {})

        except NotFoundError:
            logger.warning(f"Index {index_name} not found")
            return {}
        except Exception as e:
            logger.error(f"Failed to aggregate in {index_name}: {e}")
            return {}

    async def bulk_index(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Bulk index documents."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            if not documents:
                return True

            # Prepare bulk data
            bulk_data = []
            for doc in documents:
                # Add timestamp if not present
                if "timestamp" not in doc:
                    doc["timestamp"] = datetime.utcnow().isoformat()

                bulk_data.append({"index": {"_index": index_name}})
                bulk_data.append(doc)

            result = await self.client.bulk(body=bulk_data)

            # Check for errors
            if result.get("errors"):
                error_count = sum(1 for item in result["items"] if "error" in item.get("index", {}))
                logger.warning(f"Bulk index completed with {error_count} errors")
                return error_count == 0

            logger.info(f"Successfully bulk indexed {len(documents)} documents to {index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to bulk index documents in {index_name}: {e}")
            return False

    async def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            await self.client.delete(index=index_name, id=doc_id)
            logger.debug(f"Deleted document {doc_id} from {index_name}")
            return True

        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in {index_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id} from {index_name}: {e}")
            return False

    async def update_document(
        self, index_name: str, doc_id: str, updates: Dict[str, Any]
    ) -> bool:
        """Update a document."""
        try:
            if not self.client:
                raise ValueError("Elasticsearch client not connected")

            # Add update timestamp
            updates["last_updated"] = datetime.utcnow().isoformat()

            await self.client.update(
                index=index_name, id=doc_id, body={"doc": updates}
            )
            logger.debug(f"Updated document {doc_id} in {index_name}")
            return True

        except NotFoundError:
            logger.warning(f"Document {doc_id} not found in {index_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to update document {doc_id} in {index_name}: {e}")
            return False


# Global Elasticsearch client instance
es_client = ElasticsearchClient()
