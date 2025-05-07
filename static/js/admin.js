// admin.js

// При загрузке страницы загружаем группы
window.onload = () => {
    fetch('/api/groups')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('group-select');
            data.groups.forEach(group => {
                const option = document.createElement('option');
                option.value = group.chat_id;
                option.textContent = group.chat_id;
                select.appendChild(option);
            });
        })
        .catch(err => console.error("Ошибка загрузки групп:", err));
};

async function getParticipants() {
    const chatId = document.getElementById("group-select").value.trim();
    if (!chatId) {
        alert("Выберите группу из списка");
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