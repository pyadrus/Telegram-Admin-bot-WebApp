// admin.js

// Общая функция для заполнения select
function populateSelect(url, selectId) {
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">-- Выберите группу --</option>';

            // Проверяем, есть ли нужный ключ
            const groups = data.chat_title || data.groups || [];

            groups.forEach((group) => {
                const option = document.createElement("option");
                option.value = group.chat_title;
                option.textContent = group.chat_title;
                select.appendChild(option);
            });
        })
        .catch((err) => console.error(`Ошибка загрузки ${selectId}:`, err));
}

// При загрузке страницы
window.onload = () => {
// Получаем user_id из глобальной переменной, переданной в шаблоне
    const userId = CURRENT_USER_ID;

    populateSelect(`/chat_title?user_id=${userId}`, "group-select"); // Выбор группы, для получения количества участников
    populateSelect("/chat_title", "groups-select");
    populateSelect("/chat_title", "groups-selected");
    populateSelect("/chat_title", "groups-selecteds");
    populateSelect("/chat_title", "groups-select-privilage");
};

// Получение количества участников групп / каналов
async function getParticipants() {

    const chat_title = document.getElementById("group-select").value.trim();
    if (!chat_title) {
        alert("Выберите группу из списка");
        return;
    }

    try {
        const response = await fetch(
            `/update-participants?chat_title=${encodeURIComponent(chat_title)}`
        );
        const data = await response.json();
        const statusEl = document.getElementById("participants-count");

        if (data.success) {
            statusEl.innerText = `Участников: ${data.participants_count}`;
            statusEl.className = "status success";
        } else {
            throw new Error("Ошибка получения данных");
        }
    } catch (error) {
        document.getElementById("participants-count").innerText =
            "Не удалось получить количество участников";
        document.getElementById("participants-count").className = "status error";
    }
}




// Установка ограничения по подписке между двумя группами
async function toggleSubscriptionRequirement() {
    const chat_title = document.getElementById("groups-selected").value.trim(); // группа, которую будем ограничивать
    const required_chat_title = document
        .getElementById("groups-selecteds")
        .value.trim(); // группа, на которую нужно подписаться

    if (!chat_title || !required_chat_title) {
        alert("Выберите обе группы");
        return;
    }

    try {
        // Отправляем два параметра: chat_title и required_chat_title
        const response = await fetch(
            `/require-subscription?chat_title=${encodeURIComponent(
                chat_title
            )}&required_chat_title=${encodeURIComponent(required_chat_title)}`
        );
        const result = await response.json();

        if (result.success) {
            alert(result.message);
        } else {
            throw new Error(result.error || "Неизвестная ошибка");
        }
    } catch (error) {
        console.error("Ошибка:", error);
        alert("Не удалось сохранить настройки ограничений.");
    }
}

// Сохранение запрещённых слов в базу данных
async function saveBadWords() {
    const inputField = document.getElementById("bad-words");
    const bad_word = inputField.value.trim();

    try {
        const response = await fetch(
            `/set-bad-words?bad_word=${encodeURIComponent(bad_word)}`
        );
        const result = await response.json();

        // Очистить поле ввода
        inputField.value = "";

        // Показать сообщение пользователю
        alert("Запрещённое слово успешно сохранено!");
    } catch (error) {
        console.error("Ошибка:", error);
        alert("Не удалось сохранить запрещенные слова.");
    }
}

// Функция вызова API
async function givePrivilege() {
    const chat_title = document
        .getElementById("groups-select-privilage")
        .value.trim();
    const user_id = document.getElementById("user-id-privilege").value.trim();

    if (!chat_title || !user_id) {
        alert("Заполните все поля");
        return;
    }

    try {
        const response = await fetch(
            `give-privileges?chat_title=${encodeURIComponent(
                chat_title
            )}&user_id=${encodeURIComponent(user_id)}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    chat_title: chat_title,
                    user_id: user_id,
                }),
            }
        );

        const result = await response.json();

        if (result.success) {
            alert(result.message);
        } else {
            alert("Ошибка: " + (result.error || "Неизвестная ошибка"));
        }
    } catch (err) {
        console.error("Ошибка сети:", err);
        alert("Не удалось выполнить запрос");
    }
}
