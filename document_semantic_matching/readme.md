Running test:
    pytest -v

Generating requirement.txt:
>pipreqs . --force --savepath requirements.txt


>docker build -t doc-semantic-matching .

if you are running directly on windows
>docker run -d  -p 8000:8000 -e GEMINI_API_KEY=<yourkey> --name doc-semantic-matching doc-semantic-matching:latest

if you are running pgvector on another docker , grab it's network, and docker name
>docker run -d --name doc-semantic-matching --network <your_pgvector_default_network> -p 8000:8000  -e GEMINI_API_KEY=<yourkey> -e DB_DSN=postgresql://user:password@<your_pgvector_docker_name>:5432/wine_review_gemini  TABLE_NAME=test_test doc-semantic-matching:latest