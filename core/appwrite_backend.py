import logging
import os
from typing import Iterable

from appwrite.client import Client
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://sfo.cloud.appwrite.io/v1"
DEFAULT_PROJECT_ID = "6966f58000347a48517f"
DEFAULT_DATABASE_ID = "6966f80700332980dc4e"


def is_appwrite_configured() -> bool:
    return bool(os.getenv("APPWRITE_API_KEY"))


def get_databases() -> Databases:
    endpoint = os.getenv("APPWRITE_ENDPOINT", DEFAULT_ENDPOINT)
    project_id = os.getenv("APPWRITE_PROJECT_ID", DEFAULT_PROJECT_ID)
    api_key = os.getenv("APPWRITE_API_KEY")
    if not api_key:
        raise RuntimeError("APPWRITE_API_KEY is required for Appwrite operations.")

    client = Client()
    client.set_endpoint(endpoint)
    client.set_project(project_id)
    client.set_key(api_key)
    return Databases(client)


def get_database_id() -> str:
    return os.getenv("APPWRITE_DATABASE_ID", DEFAULT_DATABASE_ID)


def _ensure_database(databases: Databases) -> None:
    database_id = get_database_id()
    try:
        databases.get(database_id)
    except AppwriteException as exc:
        if exc.code != 404:
            raise
        databases.create(database_id=database_id, name="HexProbe")


def _ensure_collection(
    databases: Databases,
    collection_id: str,
    name: str,
    attributes: Iterable[callable],
    indexes: Iterable[callable],
) -> None:
    database_id = get_database_id()
    try:
        databases.get_collection(database_id=database_id, collection_id=collection_id)
        return
    except AppwriteException as exc:
        if exc.code != 404:
            raise

    databases.create_collection(
        database_id=database_id,
        collection_id=collection_id,
        name=name,
        permissions=[],
        document_security=True,
    )
    for create_attribute in attributes:
        create_attribute()
    for create_index in indexes:
        create_index()


def _knowledge_patterns_schema(databases: Databases) -> None:
    database_id = get_database_id()
    collection_id = "patterns"

    attributes = [
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="category",
            size=64,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="description",
            size=2048,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="severity",
            size=32,
            required=False,
        ),
        lambda: databases.create_integer_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="trigger_count",
            required=False,
        ),
        lambda: databases.create_integer_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="false_positive_count",
            required=False,
        ),
        lambda: databases.create_datetime_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="created_at",
            required=False,
        ),
    ]

    indexes = [
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="category_idx",
            type="key",
            attributes=["category"],
        ),
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="severity_idx",
            type="key",
            attributes=["severity"],
        ),
    ]

    _ensure_collection(
        databases=databases,
        collection_id=collection_id,
        name="Patterns",
        attributes=attributes,
        indexes=indexes,
    )


def _knowledge_probe_lineage_schema(databases: Databases) -> None:
    database_id = get_database_id()
    collection_id = "probe_lineage"

    attributes = [
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="pattern_id",
            size=64,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="bug_id",
            size=128,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="fix_commit",
            size=128,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="originating_repo",
            size=256,
            required=False,
        ),
        lambda: databases.create_datetime_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="created_at",
            required=False,
        ),
    ]

    indexes = [
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="pattern_idx",
            type="key",
            attributes=["pattern_id"],
        )
    ]

    _ensure_collection(
        databases=databases,
        collection_id=collection_id,
        name="Probe Lineage",
        attributes=attributes,
        indexes=indexes,
    )


def _global_patterns_schema(databases: Databases) -> None:
    database_id = get_database_id()
    collection_id = "global_patterns"

    attributes = [
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="category",
            size=64,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="description",
            size=2048,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="severity",
            size=32,
            required=False,
        ),
        lambda: databases.create_integer_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="trigger_count",
            required=False,
        ),
        lambda: databases.create_integer_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="false_positive_count",
            required=False,
        ),
        lambda: databases.create_datetime_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="created_at",
            required=False,
        ),
    ]

    indexes = [
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="global_category_idx",
            type="key",
            attributes=["category"],
        ),
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="global_severity_idx",
            type="key",
            attributes=["severity"],
        ),
    ]

    _ensure_collection(
        databases=databases,
        collection_id=collection_id,
        name="Global Patterns",
        attributes=attributes,
        indexes=indexes,
    )


def _global_probe_lineage_schema(databases: Databases) -> None:
    database_id = get_database_id()
    collection_id = "probe_lineage_global"

    attributes = [
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="pattern_id",
            size=64,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="bug_id",
            size=128,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="fix_commit",
            size=128,
            required=False,
        ),
        lambda: databases.create_string_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="originating_repo",
            size=256,
            required=False,
        ),
        lambda: databases.create_datetime_attribute(
            database_id=database_id,
            collection_id=collection_id,
            key="created_at",
            required=False,
        ),
    ]

    indexes = [
        lambda: databases.create_index(
            database_id=database_id,
            collection_id=collection_id,
            key="global_pattern_idx",
            type="key",
            attributes=["pattern_id"],
        )
    ]

    _ensure_collection(
        databases=databases,
        collection_id=collection_id,
        name="Global Probe Lineage",
        attributes=attributes,
        indexes=indexes,
    )


def init_knowledge_schema() -> bool:
    if not is_appwrite_configured():
        logger.info("Appwrite API key not configured; skipping knowledge schema.")
        return False
    databases = get_databases()
    _ensure_database(databases)
    _knowledge_patterns_schema(databases)
    _knowledge_probe_lineage_schema(databases)
    return True


def init_global_schema() -> bool:
    if not is_appwrite_configured():
        logger.info("Appwrite API key not configured; skipping global schema.")
        return False
    databases = get_databases()
    _ensure_database(databases)
    _global_patterns_schema(databases)
    _global_probe_lineage_schema(databases)
    return True
