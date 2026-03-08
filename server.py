from flask import Flask, jsonify
import vk_api
import time
import re
import os
import traceback

TOKEN = os.getenv("VK_TOKEN")
print("TOKEN:", TOKEN[:15])
PEER_ID = int(os.getenv("PEER_ID", 176781096))

app = Flask(__name__)

vk = vk_api.VkApi(token=TOKEN)
vk._auth_token()


def get_norm():
    try:
        # Отправляем команду
        vk.method("messages.send", {
            "peer_id": PEER_ID, 
            "message": "/ast Roman_Plekhanov 12 0", 
            "random_id": 0
        })

        time.sleep(3)

        history = vk.method("messages.getHistory", {"peer_id": PEER_ID, "count": 5})

        for msg in history["items"]:
            text = msg["text"]
            
            # Ищем именно блок с зафиксированными данными
            if "Зафиксированные данные" in text:
                # Отрезаем всё, что выше "Зафиксированные данные", чтобы не цеплять "Мин. норму"
                data_part = text.split("Зафиксированные данные")[1]
                
                # Ищем цифры только в этой части текста
                report_match = re.search(r"REPORT\s*=\s*(\d+)", data_part)
                z_match = re.search(r"/Z\s*=\s*(\d+)", data_part)
                online_match = re.search(r"ONLINE\s*=\s*([\dчм ]+)", data_part)

                if report_match and z_match and online_match:
                    report = int(report_match.group(1))
                    z = int(z_match.group(1))
                    online = online_match.group(1).strip()

                    # Плюсуем зетки и репорты
                    total = report + z
                    
                    # Условия нормы: 100 всего и 3 часа онлайна
                    # Парсим часы из строки типа "4ч 27м"
                    hours_match = re.search(r"(\d+)ч", online)
                    hours = int(hours_match.group(1)) if hours_match else 0
                    
                    if total >= 100 and hours >= 3:
                        return f"Норма выполнена! У вас {total} (Z+Rep) и онлайн {online}."
                    else:
                        # Считаем, чего не хватает
                        rep_left = max(0, 100 - total)
                        time_left = "и нужно еще поднять онлайн до 3ч" if hours < 3 else ""
                        return f"У вас {total} ответов и онлайн {online}. До нормы: {rep_left} отв. {time_left}"

        return "Не удалось найти сообщение с данными."

    except Exception as e:
        traceback.print_exc()
        return f"Ошибка: {e}"


@app.route("/", methods=["GET"])
def home():
    result = get_norm()
    return jsonify({"text": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

