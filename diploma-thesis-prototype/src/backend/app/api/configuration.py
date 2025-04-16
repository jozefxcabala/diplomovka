from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from backend.app.models.configuration_models import AnalysisConfigIn, AnalysisConfigOut, UpdateAnalysisConfigRequest, LinkIn
from backend.app.services.configuration_service import (
    save_analysis_config,
    get_all_analysis_configs,
    get_analysis_config_by_id,
    delete_configuration_by_id,
    update_analysis_config,
    link_analysis_with_config
)

router = APIRouter()

@router.post("/configuration", response_model=None, status_code=201)
def create_analysis_config(config: AnalysisConfigIn):
    try:
        config_id = save_analysis_config(config)
        return JSONResponse(
            status_code=201,
            content={"config_id": config_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration", response_model=List[AnalysisConfigOut], status_code=200)
def list_analysis_configs():
    try:
        return get_all_analysis_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/configuration/{config_id}", response_model=AnalysisConfigOut, status_code=200)
def get_config_by_id(config_id: int):
    try:
        config = get_analysis_config_by_id(config_id)
        if config is None:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/configuration/{config_id}", status_code=200)
async def delete_configuration(config_id: int):
    try:
        config = delete_configuration_by_id(config_id)
        if config is None:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return {
            "status": "success",
            "message": f"Configuration '{config['name']}' deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configuration/{config_id}")
async def update_configuration(config_id: int, update: UpdateAnalysisConfigRequest):
    try:
        updated = update_analysis_config(config_id, update)
        if not updated:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return {
            "status": "success",
            "message": f"Configuration '{update.name}' updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/configuration/link", response_model=None, status_code=201)
def link(link: LinkIn):
    try:
        response = link_analysis_with_config(link)
        return JSONResponse(
            status_code=201,
            content={
                "config_id": response["config_id"],
                "video_id": response["video_id"],
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))