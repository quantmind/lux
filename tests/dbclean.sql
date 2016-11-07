copy(select 'drop database ' || datname || ';'  from pg_database where datname ilike 'testlux%') to '/tmp/drop_db.sql';
\i /tmp/drop_db.sql
