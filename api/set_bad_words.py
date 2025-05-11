from fastapi import APIRouter

from utils.models import BadWords

router = APIRouter()


@router.get("/api/chat/set-bad-words")
async def write_bad_words(bad_word: str):
    """
    Записываем плохое слово в базу данных
    """
    try:
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        bad_words = BadWords(
            bad_word=bad_word.strip().lower(),  # Получаем слово от пользователя
        )
        bad_words.save()
    except Exception as e:
        return {"success": False, "error": str(e)}
