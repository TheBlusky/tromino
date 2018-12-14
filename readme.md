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

### Development / Testing

You can set your own development environment, either for adding some feature, or simply to run tests.

In order to do it, simple use the following command:

```
docker-compose build
./run_tests.sh # Linux / Darwin
run_tests.bat # Windows
```

You don't need to re-build the project to run tests when modifying source code, as `run_tests` script mount
the `./src/` directory directly into the container in order to have up-to-date source code. However, if you
change `requirements.txt`, you will need to rebuild the image in order to have dependencies installed.
