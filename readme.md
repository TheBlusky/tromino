# Tromino

*A `tromino` [wikipedia](https://en.wikipedia.org/wiki/Tromino) is a polygon made of three equal-sized squares... but
it's also an anagram of `monitor`.*

`Tromino` is a tool pluggable between Mattermost (or Slack) and anything you want to monitor.

## How to use

### Installation

```
docker run -d -v /my/own/datadir:/data/db --name tromino_mongo mongo:latest
docker run -d -p 8080 --link tromino_mongo:mongo --name tromino_tromino theblusky/tromino:latest
```
or tweak and use provided `docker-compose.yml` file.

Warning: this configuration expose `Tromino` in cleartext HTTP, you will need to use some reverse proxy (nginx, apache,
traefik, ...) in order to secure communication using HTTPS.

### Setup

Everything is performed on Mattermost :

- Create a new `slash`, called `/tromino`, targetting `http(s)://your-tromino-instance:(8080/443)/mattermost`,
- Create a new `incoming webhook`,
- Use the following command: `/tromino config setup [INCOMING WEBHOOK URL]`

And that's it ! You can use `/tromino help` to see all the commands.
