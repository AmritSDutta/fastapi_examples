import json
import requests


def _get_messy_text():
    return """This is a test passage:
        - with "quotes"
        - with emojis 😃🔥
        - with unicode অ आ あ
        - with JSON-like {bad: 'json'}
        - with newlines and \t tabs

        - def __init__(self, base_url: str):
            self.endpoint = f"{base_url}/classify"
            self.headers = {"Content-Type": "application/json"}

        - 😃🔥✨🚀📚🧠💡🔍🎯⚡📝🤖🌟💭🪄
        - এটা একটা সুন্দর বাংলা বাক্য, যা এক লাইনে আপনার জন্য লেখা হলো।
        """


if __name__ == "__main__":
    url = "http://localhost:8000/api/docs/classify"
    messy_text = _get_messy_text()

    payload = (json.dumps(
        {"passage": messy_text},
        ensure_ascii=False
    ).encode("utf-8"))

    r = requests.post(url,
                      data=payload,
                      headers={"Content-Type": "application/json"}
                      )
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
