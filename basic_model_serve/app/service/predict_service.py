import asyncio
from typing import List

import numpy as np


async def predict_async(model, features: list[float]):
    loop = asyncio.get_running_loop()
    X = np.array(features).reshape(1, -1)
    prediction: List[int] = await loop.run_in_executor(None, model.predict, X)
    return int(prediction[0])
