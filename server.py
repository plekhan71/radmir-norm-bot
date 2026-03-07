from flask import Flask, jsonify
import vk_api
import time
import re
import os
import traceback

# Токен берём из Environment Variables (на Railway: VK_TOKEN)
TOKEN = os.getenv("VK_TOKEN")
PEER_ID = int(os.getenv("PEER_ID", 176781096))

app = Flask(__name__)

# Инициализация VK API
vk = vk_api.VkApi(token=TOKEN)
vk._auth_token()

def get_norm():
    try:
        # Отправка команды боту
        vk.method("messages.send", {
            "peer_id": PEER_ID,
            "message": "/ast Roman_Plekhanov 12 0",
            "random_id": 0
        })

        time.sleep(3)

        history = vk.method("messages.getHistory", {
            "peer_id": PEER_ID,
            "count": 5
        })

        for msg in history["items"]:
            text = msg["text"]

            if "REPORT" in text:
                # Безопасный поиск чисел
                m_report = re.search(r"REPORT = (\d+)", text)
                m_z = re.search(r"/Z = (\d+)", text)
                m_online = re.search(r"ONLINE = (.+)", text)

                if m_report and m_z and m_online:
                    report = int(m_report.group(1))
                    z = int(m_z.group(1))
                    online = m_online.group(1)

                    total = report + z

                    if total >= 100:
                        return f"У вас {total} ответов и онлайн {online}. Норма выполнена."
                    else:
                        left = 100 - total
                        return f"У вас {total} ответов и онлайн {online}. До нормы осталось {left} ответов."

        # Если REPORT не найден
        return "Не удалось получить данные о REPORT."

    except Exception:
        traceback.print_exc()
        return "Произошла ошибка при получении данных."

@app.route("/", methods=["GET"])
def home():
    result = get_norm()
    return jsonify({"text": result})

# Локальный запуск для теста
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
