cd ./backend\Year3_dev_Backend/main/Year3/
chmod +x ./entrypoint.sh
docker cp ./backup_db.sql server-my-postgres-1:/tmp/backup_db.sql
docker exec -it server-my-postgres-1 bash
psql -U year3 -d smartfarm
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
exit
cd tmp
psql -U year3 -d smartfarm -f backup_db.sql
