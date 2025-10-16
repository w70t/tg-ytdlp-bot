import os
import threading
from flask import Flask

# Import the main bot logic
import magic

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Bot is running!'

def start_bot():
    magic.app.run()

if __name__ == '__main__':
    # Start the Telegram bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Start the Flask web server for Koyeb health checks
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

