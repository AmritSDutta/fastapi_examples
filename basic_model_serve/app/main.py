import asyncio
import logging
from contextlib import asynccontextmanager

import joblib
import wandb
from fastapi import FastAPI

from config.Settings import get_settings, get_run_id
from app.schemas.request_response import PredictRequest, PredictResponse, ErrorResponse
from app.service.predict_service import predict_async

logger = logging.getLogger(__name__)
app_name = get_settings().APP_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Initialize wandb run for inference ---

    run = wandb.init(
        project="ml-fastapi-wandb",
        job_type="inference",
        name=get_run_id(f'inference-{app_name}'),
        config={
            "architecture": "RandomForestClassifier",
            "dataset": "iris dataset",
            "n_estimators": 100,
        })

    # --- Download latest model artifact ---
    artifact = run.use_artifact("iris-model:latest", type="model")
    model_dir = artifact.download()

    # --- Load model asynchronously (non-blocking) ---
    model_path = f"{model_dir}/model.joblib"
    app.state.model = await asyncio.to_thread(joblib.load, model_path)
    app.state.wandb_run = run  # optional: keep handle if you log predictions

    logger.info(f"Loaded model from {model_path}")
    logging.info("model_dump:", get_settings().model_dump())

    # --- Yield to start API ---
    yield

    # --- Cleanup on shutdown ---
    run.finish()
    del app.state.model


app = FastAPI(title=app_name, lifespan=lifespan)


@app.post("/predict",
          response_model=PredictResponse,
          responses={400: {"model": ErrorResponse, "description": "Bad Request — features must be length 4"}})
async def predict(req: PredictRequest):
    logger.info(f'shape of input: {len(req.features)}, data: {req.features}')
    prediction = await predict_async(app.state.model, req.features)
    return PredictResponse(prediction=prediction)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
