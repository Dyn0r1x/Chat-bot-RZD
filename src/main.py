from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from model.model import get_text_embedding
from pdfreader import extractText

app = FastAPI()

qdrant = QdrantClient(url="http://localhost:6333")

app.add_middleware(
    CORSMiddleware,  # Класс мидлвари должен быть передан первым аргументом
    allow_origins=["http://localhost:5173"],  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешенные методы
    allow_headers=["*"],  # Разрешенные заголовки
)

embedding_dim = 300  # размерность эмбеддинга

collection_name = "test1_collection"

# Проверяем, существует ли коллекция
if not qdrant.collection_exists(collection_name=collection_name):
    # Создаем коллекцию, если она не существует
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=embedding_dim, distance=Distance.COSINE),
    )
    print(f"Коллекция {collection_name} создана.")
else:
    print(f"Коллекция {collection_name} уже существует.")

# Загружаем индекс, если он существует
# try:
#   index.load(index_path)
# except Exception as e:
#   print(f"Не найден файл индексов Annoy: {e}")

# Определение модели данных, которая описывает входные данные (JSON)
class Message(BaseModel):
  text: str  # Ожидаемое поле "text" в JSON

extracted_paragraphs = extractText("documents/Col_dogovor.pdf")

# Фильтрация пустых строк из списка параграфов
filtered_paragraphs = [p for p in extracted_paragraphs if p.strip()]
#print(filtered_paragraphs[5])

# Векторизация параграфов и сохранение в qdrant
for idx, paragraph in enumerate(filtered_paragraphs):
  # Проверка, существует ли уже этот эмбеддинг в Qdrant
  existing_points = qdrant.search(
    collection_name=collection_name,
    query_vector=get_text_embedding(paragraph),  # или используем id, если он уникальный
    limit=1
  )
  
  # Если в коллекции нет похожих точек, сохраняем
  if not existing_points:
    # Создание эмбеддинга 1 параграфа из массива отфильтрованых параграфов
    embedding = get_text_embedding(paragraph)
    # Сохранение текста и эмбеддинга в qdrant
    try:
      operation_info = qdrant.upsert(
        collection_name=collection_name,
        wait=True,
        points = [
          PointStruct(id=idx, vector=embedding, payload={"text": paragraph})
        ],
      )
      print(operation_info)
    except Exception as e:
      print(f"Ошибка при сохранении в qdrant: {e}")
  else:
    print(f"Эмбеддинг для параграфа {idx} уже существует, пропускаем сохранение.")

@app.post("/question")
async def question(message: Message):
  # print(message)
  # Векторизация вопроса пользователя
  question_embedding = get_text_embedding(message.text)
  # print(question_embedding)

  # Поиск ближайших 3 абзацев
  search_result = qdrant.query_points(
                      collection_name=collection_name, 
                      query=question_embedding, 
                      limit=3,
                      )

  # TODO: суммаризатор
  
  # for result in search_result.points:
    # print(result.payload['text'])
  
  result = ''
  texts = [point.payload['text'] for point in search_result.points]
  for i in range(0, len(texts)):
    result += texts[i]
  
  # Возвращаем ответ в формате JSON
  return result