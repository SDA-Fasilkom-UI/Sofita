All commands related to database migration from mongo to mysql.
```
docker-compose exec web bash
docker-compose exec worker bash
docker-compose exec mysql bash

python3 manage.py dumpdata > <filename>
python3 manage.py runscript scripts.mysql_migration.clean_pk --script-args <filename>
python3 manage.py migrate --database mysql
python3 manage.py loaddata --database mysql <cleaned_filename>

ALTER TABLE app_token ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE grader_submission ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE job_mossjob ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE job_reportjob ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;

python3 manage.py migrate --fake app zero
python3 manage.py migrate --fake grader zero
python3 manage.py migrate --fake job zero

python3 manage.py migrate --fake
```
