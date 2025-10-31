from joblib import load

MODEL_PATH: str = "models/model.joblib"


def load_local_model():
    return load(MODEL_PATH)
