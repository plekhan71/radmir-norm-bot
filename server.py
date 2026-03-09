from flask import Flask, request, jsonify, Response
import requests
import vk_api
import time
import re
import os
import traceback
import json

TOKEN = os.getenv("VK_TOKEN")
print("TOKEN:", TOKEN[:15])

PEER_ID = int(os.getenv("PEER_ID", 176781096))

app = Flask(__name__)

vk = vk_api.VkApi(token=TOKEN)
vk._auth_token()


def get_norm():
    try:
        # Отправляем команду боту
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

            if "Зафиксированные данные" in text:

                data_part = text.split("Зафиксированные данные")[1]

                report_match = re.search(r"REPORT\s*=\s*(\d+)", data_part)
                z_match = re.search(r"/Z\s*=\s*(\d+)", data_part)
                online_match = re.search(r"ONLINE\s*=\s*([\dчм ]+)", data_part)

                if report_match and z_match and online_match:

                    report = int(report_match.group(1))
                    z = int(z_match.group(1))
                    online = online_match.group(1).strip()

                    total = report + z

                    hours_match = re.search(r"(\d+)ч", online)
                    hours = int(hours_match.group(1)) if hours_match else 0

                    if total >= 100 and hours >= 3:
                        return f"Норма выполнена! У вас {total} (Z+Rep) и онлайн {online}."
                    else:
                        rep_left = max(0, 100 - total)
                        time_left = "и нужно еще поднять онлайн до 3 часов" if hours < 3 else ""
                        return f"У вас {total} ответов и онлайн {online}. До нормы осталось {rep_left} ответов {time_left}"

        return "Не удалось найти сообщение с данными."

    except Exception as e:
        traceback.print_exc()
        return f"Ошибка: {e}"


# -------------------------------
# ТВОЙ API (как было раньше)
# -------------------------------

@app.route("/", methods=["GET"])
def home():
    result = get_norm()

    return Response(
        json.dumps({"text": result}, ensure_ascii=False),
        content_type="application/json; charset=utf-8"
    )


# -------------------------------
# ENDPOINT ДЛЯ АЛИСЫ
# -------------------------------

@app.route("/alice", methods=["POST"])
def alice():

    try:

        result = get_norm()

        response = {
            "version": "1.0",
            "response": {
                "text": result,
                "tts": result,
                "end_session": False
            }
        }

        return jsonify(response)

    except Exception as e:

        traceback.print_exc()

        return jsonify({
            "version": "1.0",
            "response": {
                "text": "Произошла ошибка при получении данных.",
                "end_session": True
            }
        })
