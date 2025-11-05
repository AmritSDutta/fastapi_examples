>docker build -t ml-fastapi-wandb .
>docker run -d  -p 8000:8000 -e WANDB_API_KEY=<your_wandb_api_key> --name ml-fastapi-wandb ml-fastapi-wandb:latest
>docker logs <container_id>


running tests:
from root run following:
pytest -v