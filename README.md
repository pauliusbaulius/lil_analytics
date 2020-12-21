# lil_analytics
Message metadata analytics bot. Collects messages on write/edit/delete and displays nice graphs. 
Answers deep questions about your friends/users:

- Who nolifes the most?
- Who goes to sleep at 3am?
- Which channels are worth keeping?

Also displays nice graphs that make you feel informed and productive.

\<insert images here\>

## todo
- [ ] api and bot should have separate pipenvs
- [ ] non-root docker containers
- [ ] github actions for that free container build, lint and test
- [ ] logging
- [ ] loki exporter example for your docker spyware stack

## install && deploy
1. Create and fill out env file: `$ mv .env.example .env`
2. Run `$ docker-compose up -d`.
3. Go to [localhost:9999](https://localhost:9999) if you left default api port.
4. Enjoy your spyware bot 🤖



![lol](lol.png)