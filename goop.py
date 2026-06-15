import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# load .env
load_dotenv()
print("loaded env vars")

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("hi goop")
def message_goop(message, say):
    say("hi i'm goop")
    print("goop was hi'ed")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()