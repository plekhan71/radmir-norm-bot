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
        print("Отправляем команду /ast")

        vk.method("messages.send", {
            "peer_id": PEER_ID,
            "message": "/ast Roman_Plekhanov 12 0",
            "random_id": 0
        })

        time.sleep(4)

        print("Получаем историю сообщений")

        history = vk.method("messages.getHistory", {
            "peer_id": PEER_ID,
            "count": 10
        })

        print("История сообщений:", history)

        for msg in history["items"]:
            text = msg["text"]

            print("Сообщение:", text)

            if "REPORT" in text:

                m_report = re.search(r"REPORT\s*=\s*(\d+)", text)
                m_z = re.search(r"/Z\s*=\s*(\d+)", text)
                m_online = re.search(r"ONLINE\s*=\s*(.+)", text)

                if not m_report or not m_z or not m_online:
                    return f"Нашёл REPORT сообщение, но не смог распарсить: {text}"

                report = int(m_report.group(1))
                z = int(m_z.group(1))
                online = m_online.group(1)

                total = report + z

                if total >= 100:
                    return f"У вас {total} ответов и онлайн {online}. Норма выполнена."
                else:
                    left = 100 - total
                    return f"У вас {total} ответов и онлайн {online}. До нормы осталось {left} ответов."

        return "REPORT сообщение не найдено в последних сообщениях."

    except Exception as e:
        print("ОШИБКА:")
        traceback.print_exc()
        return f"Ошибка: {str(e)}"


@app.route("/", methods=["GET"])
def home():
    result = get_norm()
    return jsonify({"text": result})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

