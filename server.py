from flask import Flask, jsonify
import vk_api
import time
import re

TOKEN = "vk1.a.oCwMFpkXoHq7gs04Rmv3OsoNym8xQW_KQV6DFfYLS8tviQ0jdqMOb3DMbfThS5zdQnwXx3-R5Sl1YwYai-r0F1M8JdEkcfFBwAmiOVXrDiHLLeeEiLyPdg4qVm4zq4Hg1-zEYHKLWfp2YKwm7EY5uBZduMytPY8p6syrRTKCc03HRlti8Cx1c9MjqStnL3EiHPZXlv0xgmL7D3jYCHnWkA"
PEER_ID = 176781096

app = Flask(__name__)

vk = vk_api.VkApi(token=TOKEN)
vk._auth_token()

def get_norm():

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

            report = int(re.search(r"REPORT = (\d+)", text).group(1))
            z = int(re.search(r"/Z = (\d+)", text).group(1))
            online = re.search(r"ONLINE = (.+)", text).group(1)

            total = report + z

            if total >= 100:
                return f"У вас {total} ответов и онлайн {online}. Норма выполнена."

            else:
                left = 100 - total
                return f"У вас {total} ответов и онлайн {online}. До нормы осталось {left} ответов."


@app.route("/", methods=["GET"])
def home():

    result = get_norm()

    return jsonify({
        "text": result
    })
