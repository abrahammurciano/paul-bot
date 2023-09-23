1. Check how many polls are being kept

```sql
select count(*) from polls where not closed and (expires is not null or id > 12359);
```

2. Delete all closed polls and old polls that don't expire
```sql
delete from polls where closed or (expires is null and id < 12359);
```

3. Make a backup of all the data that remained
```sh
pg_dump --host=$HOST --username=$USERNAME --dbname=$USERNAME | sed -e "s/$USERNAME/CURRENT_USER/g" > paul_data.sql
```

4. Delete the instance, and create it again, then restore the data.
```sh
psql --host=$HOST --username=$USERNAME --dbname=$USERNAME --file paul_data.sql
```

5. Update the server to use the correct credentials with [the website](https://fly.io/apps/paul/secrets) or with the CLI.
```sh
fly secrets set DATABASE_URL=...
```

6. From the root of the repository, run the deploy command to relaunch the bot.
```sh
cd path/to/clone/of/paul-bot
fly deploy
```

7. Grant access to all the tables
```sql
GRANT INSERT, UPDATE ON TABLE allowed_editors, allowed_voters, allowed_vote_viewers, options, polls, votes to CURRENT_USER;
```