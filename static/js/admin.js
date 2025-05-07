// admin.js

// Пример функции получения количества участников
async function getParticipants() {
    const chatId = document.getElementById("chat-id").value.trim();
    if (!chatId) {
        alert("Введите ID группы или канала");
        return;
    }

    try {
        const response = await fetch(`/api/get-participants?chat_id=${encodeURIComponent(chatId)}`);
        const data = await response.json();
        const statusEl = document.getElementById("participants-count");
        if (data.success) {
            statusEl.innerText = `Участников: ${data.participants_count}`;
            statusEl.className = "status success";
        } else {
            throw new Error("Ошибка получения данных");
        }
    } catch (error) {
        document.getElementById("participants-count").innerText = "Не удалось получить количество участников";
        document.getElementById("participants-count").className = "status error";
    }
}

// Пример функции включения/выключения ограничений на сообщения
function toggleRestrictMessages() {
    const enabled = document.getElementById("restrict-messages").checked;
    alert(`Ограничение на сообщения: ${enabled ? 'ВКЛ' : 'ВЫКЛ'}`);
}

// Пример функции включения/выключения подписки
function toggleSubscriptionRequirement() {
    const enabled = document.getElementById("require-subscription").checked;
    const channel = document.getElementById("required-channel").value.trim();
    if (enabled && !channel) {
        alert("Укажите ID канала");
        return;
    }
    alert(`Требование подписки: ${enabled ? 'ВКЛ' : 'ВЫКЛ'} | Канал: ${channel}`);
}

// Пример функции сохранения запрещённых слов
function saveBadWords() {
    const words = document.getElementById("bad-words").value.trim();
    if (!words) {
        alert("Введите хотя бы одно слово");
        return;
    }
    alert(`Запрещённые слова сохранены: ${words}`);
}

// Пример функции управления контентом
function toggleContentControls() {
    const blockLinks = document.getElementById("block-links").checked;
    const blockStickers = document.getElementById("block-stickers").checked;
    const blockForwards = document.getElementById("block-forwards").checked;

    alert(`Настройки сохранены:
Ссылки: ${blockLinks ? 'заблокированы' : 'разрешены'}
Стикер: ${blockStickers ? 'заблокированы' : 'разрешены'}
Пересылка: ${blockForwards ? 'заблокирована' : 'разрешена'}`);
}