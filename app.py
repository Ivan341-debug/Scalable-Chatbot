import psycopg2
from flask import Flask
from services.webhook import webhook_handler
from config import DB_USER, DB_HOST, DB_NAME, DB_PASSWORD

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    return webhook_handler()


if __name__ == "__main__":
    app.run(port=5000, debug=True)