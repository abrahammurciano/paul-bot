# Contributing to Paul

In order to get up and running with this project, you need to first clone the repository.

```sh
$ git clone https://github.com/abrahammurciano/paul-bot.git
```

Then, you need to create a development environment with the dependencies installed. (You need to already have uv installed for this command to work.)

```sh
$ uv sync
```

You obviously need to create a Discord bot to get a token.

You must create a database if you want to run the bot locally. You can use https://www.elephantsql.com/ for that. Once you have the database, run `paul/data/schema.psql` on that database to create the necessary database schema.
```sh
$ psql -h hostname -d databasename -U username -f paul_bot/data/schema.psql
```

You will then need to add the following settings to your `.env` file to configure the bot.

```
BOT_TOKEN=<Your bot token goes here.>
DATABASE_URL=<Your database URL goes here.>
ERR_CHANNEL=<Optional. The ID of a Discord channel where the bot will send errors to.>
DBG_CHANNEL=<Optional. The ID of a Discord channel where the bot will send debug messages to.>
MAX_DB_CONNECTIONS=<Optional. The maximum number of database connections to open. This depends on your database hosting plan.>
```

Finally, you can run the bot:
```sh
$ uv run paul
```