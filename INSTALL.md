## Installation

wget https://storage.yandexcloud.net/natasha-navec/packs/navec_hudlit_v1_12B_500K_300d_100q.tar

python -m venv .venv

source .venv/bin/activate

// uvicorn backend.main:app --reload

// python src/main.py

fastapi dev src/main.py

docker compose up -d

npm run dev

docker compose stop