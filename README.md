# goop
goop is very goopy, i love goop.

goop is intended to be yet another personal to-do slack bot, but goopy.
i feel like i can make it something more, something... goopy.

## how to run
First, prepare your slack application, take the app token, and bot token.  
Your app token requires `connections:write` scope and your bot token requires `canvases:read canvases:write chat:write groups:history channels:history` scopes.
Then, take your own user ID, and a to-do canvas ID and the section ID of where you want to insert your todo list. Secondary user is completely optional, review the code to see what it does.  
Put all of these values in their respective variables in .env.example

```bash
# clone the repo blah blah
git clone https://github.com/utkrstht/goop

# install the requirements
pip install -r requirements.txt

# rename .env.example to .env
cp .env.example .env

# run it lol
python goop.py
```

## features
- can say hi to you :3
- can ask your goals and repeat whatever you say in the thread (for now :3)
