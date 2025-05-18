"""
configuration_service.py

Service layer for managing analysis configuration data.

Functions:
- save_analysis_config: stores a new configuration in the database.
- get_all_analysis_configs: retrieves all saved configurations.
- get_analysis_config_by_id: fetches a specific configuration by its ID.
- delete_configuration_by_id: removes a configuration from the database.
- update_analysis_config: updates an existing configuration entry.
- link_analysis_with_config: associates a video with a configuration.
"""

from typing import List, Optional
from backend.app.models.configuration_models import AnalysisConfigIn, LinkIn
from backend.app.core.database_manager import DatabaseManager

# Save a new configuration to the database
def save_analysis_config(config: AnalysisConfigIn) -> int:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.insert_analysis_configuration(config.name, config.categories, config.settings)

# Retrieve all configurations from the database
def get_all_analysis_configs() -> List[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.fetch_all_analysis_configurations()

# Get configuration details by ID
def get_analysis_config_by_id(config_id: int) -> Optional[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.fetch_analysis_configuration_by_id(config_id)

# Delete a configuration by ID
def delete_configuration_by_id(config_id: int) -> Optional[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.delete_analysis_configuration_by_id(config_id)

# Update an existing configuration by ID
def update_analysis_config(config_id: int, config: AnalysisConfigIn) -> bool:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.update_analysis_configuration(config_id, config.name, config.categories, config.settings)

# Link a video with a configuration in the database
def link_analysis_with_config(link: LinkIn) -> dict:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.link_analysis_with_config(link.video_id, link.config_id)
