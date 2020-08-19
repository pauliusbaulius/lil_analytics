import pathlib

# Bot command prefix and status message. Change to your liking.
# There are way more popular bots using "." as their command prefix.
command_prefix = "."
status_message = "his database of metadata"

# Bot token. Need a token to run bot.
bot_token = ""

# Invite link. Create your own # TODO tutorial
invite_link = "https://discordapp.com/oauth2/authorize-client_id=672865567329353778&permissions=8&scope=bot"

# Your discord id. This is needed for certain commands meant to be used by the owner only!
sudoer = None

# Bot id to check whether bot is this bot.
bot_id = None

# Directory definitions. You can leave those like this.
database = "data/databases/data.db"
media = "data/media/tmp"

# Do not touch these 8-)
root_dir = pathlib.Path(__file__).parent.resolve()
github_link = "https://github.com/pauliusbaulius/lil_analytics"
