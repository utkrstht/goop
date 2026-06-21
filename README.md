# goop
goop is very goopy, i love goop.

goop is intended to be yet another personal to-do and project writing and and uhh slack bot, but goopy.
i feel like i can make it something more, something... goopy.

## how to run
### prepare 
First, prepare your slack application, take the app token, and bot token.  

Your app token requires `connections:write` scope and your bot token requires `canvases:read canvases:write chat:write groups:history channels:history` scopes.

Then, take your own user ID, a to-do canvas ID and the section ID of where you want to insert your todo list, a project canvas ID and the section ID of where you want to insert your project ideas

Secondary user and Groq API key are completely optional, they are for an easter egg for someone you wish to prank. Review the code to see what the easter egg is :3

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
- can ask your goals
- can write down your goals!
- can mark goals done as per you!
- can write down your project ideas!

## issues
- ~~goop appends the entire goal list every goal to canvas~~
- ~~goop created a new checkbox for every marked goal~~
- i forgot the rest
- goop is local, must shift to nest

## ai usage
no cap on god bro i didn't let a single LETTER from ai in this thing twin istg no cap 
i'll sacrifice my newborn if you manage to find ai in this

### latest commit name
docs: update documentation