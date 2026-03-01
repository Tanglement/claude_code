"""MongoDB database connection module."""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import Optional, Any, List, Dict
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB database connection manager."""

    def __init__(self, host: str, port: int, database: str, username: Optional[str] = None,
                 password: Optional[str] = None):
        """Initialize MongoDB connection.

        Args:
            host: MongoDB server host
            port: MongoDB server port
            database: Database name
            username: MongoDB username (optional)
            password: MongoDB password (optional)
        """
        self.host = host
        self.port = port
        self.database_name = database
        self.username = username
        self.password = password
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None

    def connect(self) -> 'MongoDBConnection':
        """Connect to MongoDB server."""
        try:
            if self.username and self.password:
                connection_string = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}"
                self.client = MongoClient(connection_string)
            else:
                self.client = MongoClient(self.host, self.port)

            self.db = self.client[self.database_name]
            logger.info(f"MongoDB connected to {self.host}:{self.port}/{self.database_name}")
            return self
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_collection(self, name: str) -> Collection:
        """Get a collection by name.

        Args:
            name: Collection name

        Returns:
            Collection instance
        """
        if self.db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db[name]

    def insert_one(self, collection: str, document: Dict) -> Any:
        """Insert a single document.

        Args:
            collection: Collection name
            document: Document to insert

        Returns:
            Inserted document id
        """
        col = self.get_collection(collection)
        result = col.insert_one(document)
        return result.inserted_id

    def insert_many(self, collection: str, documents: List[Dict]) -> List[Any]:
        """Insert multiple documents.

        Args:
            collection: Collection name
            documents: List of documents to insert

        Returns:
            List of inserted document ids
        """
        col = self.get_collection(collection)
        result = col.insert_many(documents)
        return result.inserted_ids

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find a single document.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Document or None
        """
        col = self.get_collection(collection)
        return col.find_one(query)

    def find_many(self, collection: str, query: Dict, sort: Optional[List[tuple]] = None,
                  limit: int = 0) -> List[Dict]:
        """Find multiple documents.

        Args:
            collection: Collection name
            query: Query filter
            sort: Sort specification
            limit: Maximum number of documents

        Returns:
            List of documents
        """
        col = self.get_collection(collection)
        cursor = col.find(query)

        if sort:
            cursor = cursor.sort(sort)

        if limit > 0:
            cursor = cursor.limit(limit)

        return list(cursor)

    def update_one(self, collection: str, query: Dict, update: Dict, upsert: bool = False) -> int:
        """Update a single document.

        Args:
            collection: Collection name
            query: Query filter
            update: Update operation
            upsert: Insert if not exists

        Returns:
            Number of modified documents
        """
        col = self.get_collection(collection)
        result = col.update_one(query, update, upsert=upsert)
        return result.modified_count

    def delete_one(self, collection: str, query: Dict) -> int:
        """Delete a single document.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Number of deleted documents
        """
        col = self.get_collection(collection)
        result = col.delete_one(query)
        return result.deleted_count

    def delete_many(self, collection: str, query: Dict) -> int:
        """Delete multiple documents.

        Args:
            collection: Collection name
            query: Query filter

        Returns:
            Number of deleted documents
        """
        col = self.get_collection(collection)
        result = col.delete_many(query)
        return result.deleted_count

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global MongoDB connection instance
mongodb_conn: Optional[MongoDBConnection] = None


def init_mongodb(host: str = 'localhost', port: int = 27017, database: str = 'stock_db',
                 username: Optional[str] = None, password: Optional[str] = None) -> MongoDBConnection:
    """Initialize MongoDB connection.

    Args:
        host: MongoDB server host
        port: MongoDB server port
        database: Database name
        username: MongoDB username (optional)
        password: MongoDB password (optional)

    Returns:
        MongoDBConnection instance
    """
    global mongodb_conn
    mongodb_conn = MongoDBConnection(host, port, database, username, password)
    mongodb_conn.connect()
    return mongodb_conn


def get_mongodb() -> MongoDBConnection:
    """Get the global MongoDB connection instance.

    Returns:
        MongoDBConnection instance

    Raises:
        RuntimeError: If MongoDB not initialized
    """
    if mongodb_conn is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return mongodb_conn
