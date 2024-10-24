from navec import Navec
import numpy as np

# https://github.com/natasha/navec

path = 'navec_hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)

# Функция для вычисления эмбеддинга текста
def get_text_embedding(text):
  words = text.split()  # Разбиваем текст на слова
  # Получаем эмбединги для слов
  words_embeddings = [navec[word] for word in words if word in navec]
  if words_embeddings:
    # Усредняем эмбеддинги для получения эмбеддинга текста
    return np.mean(words_embeddings, axis=0)
  else:
    # Возвращаем нулевой вектор, если нет известных слов
    return np.zeros(300)