# lil_analytics
Message metadata analytics bot. Collects messages on write/edit/delete and displays nice graphs. 
Answers deep questions about your friends/users:

- Who nolifes the most?
- Who goes to sleep at 3am?
- Which channels are worth keeping?

Will ~~Also~~ display~~s~~ nice graphs that make you feel informed and productive.

\<insert images here\>

## commands
```
.index 
    index all available messages in the guild. requires you to be the owner. 
    set owner_id in .env!
 
.kick .ban <user mention>
    your "common" commands to manage users.

.clear <int> or "all"
    delete messages in the channel. can give a number or word all.
    requires message management permissions.
    use with care. it has the ability to nuke a channel. no undo!

.gdpr <user mention>
    delete all messages in the called channel by mentioned user.
    no undo. handle with care.

.c <a;b;c>
    choose between choices separated by ";"

.8ball
    you know what 8ball is, the hello world of discord bot development.

```

## tech stack
- FastAPI serves frontend and api.
- SQLite stores indexed message metadata.
- Discord.py bot sniffs information and throws it to api.
- Makefile(the OG Action) to build, lint, clean code.
- Chart.js for dashboard graphs.


## todo features
- [ ] api and bot should have separate pipenvs
- [ ] non-root docker containers
- [ ] logging
- [ ] promtail->loki exporter example for your docker spyware stack

## install && deploy
1. Create and fill out env file: `$ mv .env.example .env`!
    1.1 You will need to create a Discord bot, or use existing one.
2. Run `$ sudo docker-compose up -d`.
3. Go to [localhost:9998](https://localhost:9998) if you left default api port.
4. Configure reverse proxy of your choice. I use NGINX, example config can be found in root dir of the project.
4. Enjoy your spyware bot 🤖
5. Do not forget to pull updates regularly. I will try to not make any breaking changes ;)

![lol](lol.png)