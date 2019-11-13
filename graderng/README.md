# Grader-NG

Data Structures and Algorithms Grader

## Development

1. Make sure Docker already installed and virtual environment already created.

1. Install Pillow and its dependencies.

   ```
   pip install Pillow
   ```

1. Install all requirements.

   ```
   pip install -r requirements.txt
   ```

1. Run MongoDB.

   ```
   docker run --rm -d -p 27017:27017 --name=test-mongo mongo
   ```

1. Run Redis.

   ```
   docker run --rm -d -p 6379:6379 --name test-redis redis
   ```

1. Run worker.

   ```
   celery -A graderng worker --loglevel=info
   ```

## Production

1. Install `docker` and `docker-compose`.

1. Create `.env` file.

   ```
   DJANGO_SECRET_KEY=thisissecretkey
   DJANGO_ENV=debug
   DJANGO_MEDIA_LOCATION=/home/user/blablabla

   MONGO_DATA_LOCATION=/home/user/mongo/gogogogo
   MONGO_DBNAME=sofita
   MONGO_USERNAME=mongousername
   MONGO_PASSWORD=mongopassword
   MONGO_HOST=mongo
   MONGO_PORT=27017

   REDIS_PASSWORD=redispwd
   REDIS_HOST=redis
   REDIS_PORT=6379

   SCELE_URL=http://172.20.0.1/webservice/rest/server.php
   SCELE_TOKEN=887bfe50daa8b8e518dd38e3832199b6
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

1. Add `grader_url` and `grader_token` variable to `config.php` at SCELE.

   ```
   $CFG->grader_url = "<grader_url>"
   $CFG->grader_token = "<grader_token>"
   ```

## Installing control groups in Linux

Isolate needs control groups feature in Linux for sandboxing contestants' programs. You need to install it:

```
sudo apt-get install cgroup-bin
```

Then, we have to enable the memory and swap accounting in control groups. Follow these steps.

1. Add swap partition to your system if it does not have any. Note that a swap partition is **mandatory** for Isolate to function properly.
1. Open the **/etc/default/grub** using sudo privilege.
1. Modify the line containing **GRUB_CMDLINE_LINUX** as follows: ::
   ```
   GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"
   ```
1. Update the GRUB:
   ```
   sudo update-grub
   ```
1. Reboot the machine.
1. Verify that either the **/sys/fs/cgroup/memory/memory.memsw.limit_in_bytes** file or **/sys/fs/cgroup/memory/memory.soft_limit_in_bytes** file exists.

Source: https://judgels.readthedocs.io/en/latest/administrator/gabriel/setup.html

## Apache

1. Enable proxy.

   ```
   sudo a2enmod proxy
   sudo service apache2 restart
   ```

1. Modify apache2 config `/etc/apache2/sites-available/000-default.conf`.

   ```
   <VirtualHost *:80>
       ProxyPreserveHost On

       ProxyPass / http://127.0.0.1:8080/
       ProxyPassReverse / http://127.0.0.1:8080/
   </VirtualHost>
   ```

1. Restart service.

   ```
   sudo service apache2 restart
   ```

## Important Notes

1. Use `sqlparse==0.2.4`
