import logging
import os
import time
import uuid

import wandb
from joblib import dump
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import sys
print(f'XXXXXXX: {sys.executable}')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ensure directory exists
os.makedirs("models", exist_ok=True)

X, y = load_iris(return_X_y=True)
logger.info(f'Data format for train: {X[:1]}, shape: {X.ndim}')
model = RandomForestClassifier(n_estimators=100).fit(X, y)
dump(model, "models/model.joblib")

# --- Unique Run Name ---
run_id = str(uuid.uuid4())[:8]  # short unique id
run_name = f"train-{time.strftime('%Y-%m-%dT%H.%M.%S')}-{run_id}"

run = wandb.init(
    project="ml-fastapi-wandb",
    job_type="train",
    name=run_name,
    config={
        "architecture": "RandomForestClassifier",
        "dataset": "iris dataset",
        "n_estimators": 100,
    })

artifact = wandb.Artifact("iris-model", type="model")
artifact.add_file("models/model.joblib")
run.log_artifact(artifact)
run.finish()
