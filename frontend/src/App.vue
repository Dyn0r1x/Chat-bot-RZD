<template>
  <div>
    <!-- Отображение всех сообщений (как пользователя, так и сервера) -->
    <div class="response-block">
      <div
        v-for="(message, index) in chatMessages"
        :key="index"
        :class="message.role"
      >
        <p>{{ message.role === "user" ? "Вы" : "Сервер" }}:</p>
        <p class="text">{{ message.text }}</p>
      </div>
    </div>

    <!-- Форма с полем ввода и кнопкой отправки -->
    <form @submit.prevent="sendMessage">
      <input
        type="text"
        v-model="question"
        @keyup.enter="sendMessage"
        placeholder="Введите сообщение"
      />
      <button type="submit" class="button">Отправить</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";

const question = ref(""); // Поле для ввода сообщения
const chatMessages = ref([]); // Поле для хранения ответа от сервера

const sendMessage = async () => {
  if (question.value.trim()) {
    chatMessages.value.push({ role: "user", text: question.value });
    try {
      // Используем fetch для отправки POST запроса на сервер
      const res = await fetch("http://127.0.0.1:8000/question/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: question.value }), // Отправляем сообщение в формате JSON
      });

      if (!res.ok) {
        alert(`Ошибка HTTP: ${res.status}. Проверьте подключение к интернету.`);
      }

      // Парсим JSON ответ от сервера
      const data = await res.json();

      // Добавляем ответ сервера в список чата
      chatMessages.value.push({ role: "bot", text: data });

      question.value = "";
    } catch (error) {
      alert(
        "Произошла непредвиденная ошибка при отправке сообщения, попробуйте позже.",
        error
      );
    }
  } else {
    alert("Введите сообщение.");
  }
};
</script>

<style scoped>
.response-block {
  width: 70%;
  height: 50%;
  padding: 20%;
  background-color: #495a6e;
  border-radius: 10px;
}
p {
  color: white;
}
.text {
  color: rgb(144, 214, 191);
}
</style>
