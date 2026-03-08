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

        # Проходим **от последнего к первому**, чтобы найти самый свежий блок "Зафиксированные данные"
        for msg in reversed(history["items"]):
            text = msg["text"]
            if "Зафиксированные данные" in text:
                report_match = re.search(r"REPORT = (\d+)", text)
                z_match = re.search(r"/Z = (\d+)", text)
                online_match = re.search(r"ONLINE = ([\dчм ]+)", text)

                if report_match and z_match and online_match:
                    report = int(report_match.group(1))
                    z = int(z_match.group(1))
                    online = online_match.group(1).strip()

                    total = report + z
                    left = max(0, 100 - total)

                    if total >= 100:
                        return f"У вас {total} ответов и онлайн {online}. Норма выполнена."
                    else:
                        return f"У вас {total} ответов и онлайн {online}. До нормы осталось {left} ответов."

        return "Не удалось получить данные о REPORT."

    except Exception as e:
        traceback.print_exc()
        return f"Произошла ошибка: {e}"


@app.route("/", methods=["GET"])
def home():
    result = get_norm()
    return jsonify({"text": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

