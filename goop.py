import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from random import randint
from copy import deepcopy
import json

# load .env
load_dotenv()
print("loaded env vars")

PRIMARY_USER = os.environ.get("PRIMARY_USER")
SECONDARY_USER = os.environ.get("SECONDARY_USER")
CANVAS_ID = os.environ.get("TODO_CANVAS_ID")
SECTION_ID = os.environ.get("TODO_SECTION_ID")

goals = []
# goals_secondary exists as a temporary copy of goals so we can access and manipulate goals without touching the primary list
goals_secondary = []
goalAsk_threads = set()
goals_done_dialog = ["wowie! you sure have some work! :woa:", "oooo that sounds interesting", "that is goopy yes", "ooooooo"]

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

##### util helpers
def say_thread(text, channel, client):
    response = client.chat_postMessage(
        channel=channel,
        text=text,
    )
    return response

def say_in_thread(text, say, channel, client, thread_ts):
    if thread_ts:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )
        return response
    else: 
        # edge cases where thread_ts MAY exist
        say(text)

##### goals management
def load_goals():
    try:
        with open("goals.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
def save_goals(goals):
    with open("goals.json", "w", encoding="utf-8") as f:
        json.dump(goals, f, indent=4)

def lookup_goal(goal):
    words = goal.split()

    # get biggest (unique?) word to prevent duplicates
    search_term = max(words, key=len)

    response = app.client.canvases_sections_lookup(
    canvas_id=CANVAS_ID,
    criteria={
        "contains_text": search_term
        }
    )

    return response["sections"][0]["id"]

def add_goal(goal):
    goals = load_goals()
    # since we do not want to touch the primary object, we make an independent copy
    goals_secondary = deepcopy(goals)

    goals_secondary.append({"goal": goal, "done": False})
    # update canvas using secondary object
    update_todo_canvas(goals_secondary)
    section_id = lookup_goal(goal)

    # add goal
    goals.append({"goal": goal, "done": False, "section_id": section_id})
    save_goals(goals)

def goals_to_markdown(goals_secondary):
    lines = []

    for goal in goals_secondary:
        checkbox = "x" if goal["done"] else " "
        lines.append(f"- [{checkbox}] {goal['goal']}")

    return "\n".join(lines)

##### goop activities
@app.message("hi goop")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("hi i'm goop", say, message["channel"], client, thread_ts)
    print("goop was hi'ed")

@app.message("goop say hi")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("hi i'm goop", say, message["channel"], client, thread_ts)
    print("goop was hi'ed")

@app.message("goop")
def message_goop(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("goopy", say, message["channel"], client, thread_ts)
    print("goop was gooped")

@app.message("goop tell vro to shut up")
def message_shutup(client, message, say):
    # if invoked in thread, it will reply in thread
    thread_ts = message.get("thread_ts") 
    say_in_thread("vro shut up", say, message["channel"], client, thread_ts)
    print("goop shut someone up")

##### todo stuff
@app.message("goop ask me my goals for today please")
def todo_create(message, client):
    # make sure no one abuses 
    if message["user"] != PRIMARY_USER:
        return
    
    # switch to using custom function
    response = say_thread(channel=message["channel"], text=f"what are your goals for today? <@{PRIMARY_USER}>", client=client)
    print("goop asked for goals")
    goalAsk_threads.add(response["ts"])

# update canvas
def update_todo_canvas(goals_secondary):
    # create checklist in form: - [ ] (goal)
    checklist = goals_to_markdown(goals_secondary)

    # edit canvas
    app.client.canvases_edit(canvas_id=CANVAS_ID, changes=[{"operation": "insert_after", "section_id": SECTION_ID, "document_content": {"type": "markdown", "markdown": f"\n{checklist}"}}])


# handle goals thread reply
@app.event("message")
def handle_todo_update(event, client, say):
    if event.get("subtype"):
        return
    
    thread_ts = event.get("thread_ts")

    # is it a thread reply?
    if not thread_ts:
        return

    # is it our thread?
    if not thread_ts in goalAsk_threads:
        return

    # is it me?
    if event.get("user") != PRIMARY_USER:
        return
    
    # goals done!
    # wow am i dumb :3
    if event.get("text").lower() in ("that's it", "that's it!", "that's all!", "that's all"):
        goalAsk_threads.remove(thread_ts)
        # say random cool thing lol
        # add custom helper for thread reply
        say_in_thread(goals_done_dialog[randint(0, len(goals_done_dialog)-1)], say, event.get("channel"), client=client, thread_ts=thread_ts)
        print("updated todo canvas")
        return
    
    print("goop saw a thread reply from kabom")
    goal = event.get("text")
    add_goal(goal)
    print(f"goop added a goal to goals: {goal}")


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()