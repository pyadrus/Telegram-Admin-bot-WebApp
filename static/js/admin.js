// admin.js

// Общая функция для заполнения select
function populateSelect(url, selectId) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">-- Выберите группу --</option>';
            data.chat_title.forEach(group => {
                const option = document.createElement('option');
                option.value = group.chat_title;
                option.textContent = group.chat_title;
                select.appendChild(option);
            });
        })
        .catch(err => console.error(`Ошибка загрузки ${selectId}:`, err));
}

// При загрузке страницы
window.onload = () => {
    populateSelect('/api/chat_title', 'group-select');
    populateSelect('/api/chat_title', 'groups-select');
};

// Получение участников
async function getParticipants() {
    const chat_title = document.getElementById("group-select").value.trim();
    if (!chat_title) {
        alert("Выберите группу из списка");
        return;
    }

    try {
        const response = await fetch(`/api/update-participants?chat_title=${encodeURIComponent(chat_title)}`);
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

// Ограничение на отправку сообщений
async function toggleRestrictMessages() {
    const chat_title = document.getElementById("groups-select").value.trim();
    if (!chat_title) {
        alert("Выберите группу из списка");
        return;
    }

    try {
        const response = await fetch(`/api/update-restrict-messages?chat_title=${encodeURIComponent(chat_title)}&restricted=true`);
        const data = await response.json();
        const statusEl = document.getElementById("participants-count");

        if (data.success) {
            statusEl.innerText = data.is_restricted
                ? `Сообщения заблокированы для "${chat_title}"`
                : `Сообщения разрешены для "${chat_title}"`;
            statusEl.className = "status success";
        } else {
            throw new Error("Ошибка установки ограничений");
        }
    } catch (error) {
        document.getElementById("participants-count").innerText = "Не удалось применить ограничения";
        document.getElementById("participants-count").className = "status error";
    }
}