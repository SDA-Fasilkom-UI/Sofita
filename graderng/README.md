# Grader-NG

Data Structures and Algorithms Grader

## Development

1. Make sure Docker already installed and virtual environment already created.
1. Add your Java binary path to `$PATH`.
1. Install all requirements.
   ```
   pip install -r requirements.txt
   ```
1. Run mysql.
   ```
   docker run --rm -d -p 3306:3306 --name=test-mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -e MYSQL_DATABASE=test mysql
   ```
1. Run Redis.
   ```
   docker run --rm -d -p 6379:6379 --name test-redis redis
   ```
1. Run worker.
   ```
   celery -A graderng worker --loglevel=info
   ```
1. Run testcase worker.
   ```
   celery -A graderng worker -Q testcase --loglevel=info
   ```
1. Run misc worker.
   ```
   celery -A graderng worker -Q misc --loglevel=info
   ```

## Production

1. Install `docker` and `docker-compose`.
1. Create **media** directory with random directory name inside it. Don't forget
   to assign `DJANGO_UPLOADS_DIRECTORY` with this name later.
1. Create **mysql** data directory.
1. Create `.env` file.

   ```
   DJANGO_SECRET_KEY=thisissecretkey
   DJANGO_ENV=debug
   DJANGO_MEDIA_LOCATION=/home/user/blablabla
   DJANGO_UPLOADS_DIRECTORY=randomdirectoryinsidemedia/

   HTTP_PROXY=

   MYSQL_DATA_LOCATION=/absolute/path/to/mysqldir
   MYSQL_DBNAME=mysqldbname
   MYSQL_USERNAME=mysqlusername
   MYSQL_PASSWORD=mysqlpassword
   MYSQL_HOST=mysql
   MYSQL_PORT=3306
   MYSQL_ROOT_PASSWORD=mysqlrootpassword

   REDIS_PASSWORD=redispwd
   REDIS_HOST=redis
   REDIS_PORT=6379

   SCELE_URL=http://172.20.0.1/webservice/rest/server.php
   SCELE_TOKEN=887bfe50daa8b8e518dd38e3832199b6

   WORKER_CONCURRENCY=2
   TESTCASE_CONCURRENCY=8
   MISC_CONCURRENCY=4
   ```

1. Run all services.
   ```
   docker-compose up -d
   ```
1. Create superuser.
   ```
   docker-compose exec web python3 manage.py createsuperuser
   ```
1. Generate token for SCELE.
1. Add `grader_url` and `grader_token` variable to `config.php` at SCELE. Do not add trailing slash to URL.
   ```
   $CFG->grader_url = '<grader_url>';
   $CFG->grader_token = '<grader_token>';
   ```

## Installing Control Groups in Linux

Isolate needs control groups feature in Linux for sandboxing submissions. You need to install it:

```
sudo apt-get install cgroup-bin
```

Then, we have to enable the memory and swap accounting in control groups. Follow these steps.

1. Add swap partition to your system if it does not have any. Note that a swap partition is **mandatory** for Isolate to function properly.
1. Open the **/etc/default/grub** using sudo privilege.
1. Modify the line containing **GRUB_CMDLINE_LINUX** as follows:
   ```
   GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"
   ```
1. Update the GRUB:
   ```
   sudo update-grub
   ```
1. Reboot the machine.
1. Verify that either the **/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes** file or **/sys/fs/cgroup/memory/memory.soft_limit_in_bytes** file exists.

Source [here.](https://judgels.readthedocs.io/en/latest/administrator/gabriel/setup.html#installing-control-groups-in-linux)

## Important Notes

1. `--privileged` is used due to https://github.com/ioi/isolate/issues/35
1. When creating media directory for docker volume binding, please specify `uid` to 1300 and `gid` to 1300.
   ```
   sudo chown -R 1300:1300 <media_dir_on_host>
   ```
