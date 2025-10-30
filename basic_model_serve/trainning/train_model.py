import wandb
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from joblib import dump
import os

# ensure directory exists
os.makedirs("models", exist_ok=True)

X, y = load_iris(return_X_y=True)
model = RandomForestClassifier(n_estimators=100).fit(X, y)
dump(model, "models/model.joblib")

run = wandb.init(project="ml-fastapi-wandb", job_type="train", name='RandomForestClassifier-iris-exp-1', config={
        "architecture": "RandomForestClassifier",
        "dataset": "iris dataset",
        "n_estimators": 100,
    })
artifact = wandb.Artifact("iris-model", type="model")
artifact.add_file("models/model.joblib")
run.log_artifact(artifact)
run.finish()
