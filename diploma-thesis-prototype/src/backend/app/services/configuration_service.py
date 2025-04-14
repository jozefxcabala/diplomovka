from typing import List, Optional
from backend.app.models.configuration_models import AnalysisConfigIn
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