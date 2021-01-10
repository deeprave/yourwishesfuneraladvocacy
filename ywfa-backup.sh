stamp=$(date +%Y%m%d_%H%M%S)
name=ywfa-${stamp}
pg_dump -f ${name}.sql -d -b -E utf-8 -c -h localhost -p 5432 -U postgres -d ywfa
ls -l ${name}.sql
grep -v '(SUBSCRIPTION|PUBLICATION)' < ${name}.sql > backups/backup_${name}
rm ${name}.sql
bzip2 -9 backups/backup_${name}
ls -l backups/backup_${name}*
