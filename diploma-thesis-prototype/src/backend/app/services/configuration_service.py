from typing import List, Optional
from backend.app.models.configuration_models import AnalysisConfigIn, LinkIn
from backend.app.core.database_manager import DatabaseManager

def save_analysis_config(config: AnalysisConfigIn) -> int:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.insert_analysis_configuration(config.name, config.categories, config.settings)

def get_all_analysis_configs() -> List[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.fetch_all_analysis_configurations()

def get_analysis_config_by_id(config_id: int) -> Optional[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.fetch_analysis_configuration_by_id(config_id)

def delete_configuration_by_id(config_id: int) -> Optional[dict]:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.delete_analysis_configuration_by_id(config_id)

def update_analysis_config(config_id: int, config: AnalysisConfigIn) -> bool:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.update_analysis_configuration(config_id, config.name, config.categories, config.settings)

def link_analysis_with_config(link: LinkIn) -> dict:
    db = DatabaseManager(db_name="diploma_thesis_prototype_db", user="postgres", password="postgres")
    db.connect()
    return db.link_analysis_with_config(link.video_id, link.config_id)
