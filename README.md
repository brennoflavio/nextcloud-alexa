# Sabiá

Sabiá is a middleware between your Nextcloud server and Alexa, allowing to access your notes, tasks, calendars and music. Also ships with an email relay so it can read your emails. Currently only Brazilian Portuguese is supported, but feel free to add new languages if you want.

# Installation

In order to run this app, you'll need to host it behind a reverse proxy and exposte a secure, https url for it to be accessed. This repository provices a `Dockerfile` and `docker-compose.yml` to run your app in a server that supports docker.

1. Create a .env file in the root of this repository, filling the variables from `.env.example`
2. Run `docker-compose build`
3. Then `docker-compose up -d`

To run it. The configuration list is explained bellow:

```
CALENDAR_URL -> Caldav Url of your main calendar
CALENDAR_NAME -> Name of your main calendar
EXTRA_CALENDARS -> Read only subscription links from other calendar providers, in ics format. Comma separated. Useful to track google calendars
NEXTCLOUD_URL -> Url of your Nextcloud instance
NEXTCLOUD_USERNAME -> Username of your Nextcloud instance
NEXTCLOUD_PASSWORD -> Password of your Nextcloud instance
TASK_URL -> Caldav Url of your Task List
TASK_LIST_NAME -> Name of your Task List
IMAP_USERNAME -> Username of your IMAP server
IMAP_PASSWORD -> Password of your IMAP server
IMAP_SERVER -> IP or domain of your IMAP server
IMAP_PORT -> Port of your IMAP server
SUBSONIC_API_URL -> Subsonic API url of your Nextcloud Music instance
SUBSONIC_USER -> Subsonic username of your Nextcloud Music instance
SUBSONIC_PASSWORD -> Subsonic password of your Nextcloud Music instance
APP_URL -> URL of this app, public accessible
ALEXA_SKILL_ID -> ID of the corresponding Alexa Skill, can be found in the console
```

# Alexa configuration

This respository provides a JSOn file with the intents to be used by this app. Go to [https://developer.amazon.com/alexa/console](https://developer.amazon.com/alexa/console), login with the same account that uses Alexa, create a new skill, name it Nextcloud, start from scratch.

Under Interaction Model > Intents > JSON Editor, replace the json with `intents.json` provided in this repository

Under Slot Types > Interfaces, enable Audio Interface

Under Slot Types > Endpoint, change from Lambda to https and enter the url of this app in your server.

Now you can save and build the skill.

Once its ready, you can test it by going to "Test", and typing:
```
Alexa, peça ao sabiá para listar eventos de hoje
```

In your echo phone app you should also see the skill there.
