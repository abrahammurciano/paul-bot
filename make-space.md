First check how many polls are being kept

```sql
select count(*) from polls where not closed and (expires is not null or id > 12359);
```

Then delete all closed polls and old polls that don't expire
```sql
delete from polls where closed or (expires is null and id < 12359);
```

Then make a backup of all the data that remained
```sh
pg_dump --host=... --username=... --dbname=... > paul_data.sql
```

Then delete the instance, and create it again, then restore the data.
```sh
psql --host=... --username=... --dbname=... --file paul_data.sql
```

Then update the server to use the correct credentials.