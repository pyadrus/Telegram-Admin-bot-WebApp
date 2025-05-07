// admin.js

// При загрузке страницы загружаем группы
window.onload = () => {
    fetch('/api/chat_title')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('group-select');
            data.chat_title.forEach(group => {  // ← здесь была ошибка
                const option = document.createElement('option');
                option.value = group.chat_title;
                option.textContent = group.chat_title;
                select.appendChild(option);
            });
        })
        .catch(err => console.error("Ошибка загрузки групп:", err));
};

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