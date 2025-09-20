from flask import Flask
from services.webhook import webhook_handler

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    return webhook_handler()


if __name__ == "__main__":
    app.run(host= '0.0.0.0',port=5000, debug=True)