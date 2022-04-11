cgitize in Docker
=================

cgitize is executed as a cron job inside the container.
The `SCHEDULE` environment variable controls how often it gets run (see below).

* Image: **egortensin/cgitize**
* Volumes:
    * `/etc/cgitize/cgitize.toml`: configuration file path.
    * `/mnt/cgitize`: by default, cloned repositories will be written here.
    * `/ssh-agent.sock`: if you use SSH, map the agent socket here.
* Environment variables:
    * `SCHEDULE`: defaults to "once", which makes the container exit after the
first run.
You can also set it to "15min", "hourly", "daily", "weekly", "monthly" or a
custom 5-part cron schedule like "*/5 * * * *".

Frontend
--------

There's a web server image with a working cgit installation.

* Image: **egortensin/cgitize-frontend**
* Volumes:
    * `/etc/cgitrc`: if you use a custom cgit configuration, map it here.
It could look like this:

           # Generally useful and opionated settings, included in the image.
           include=/etc/cgit/common

           # If you serve from a subdirectory.
           virtual-root=/custom/

           root-title=Custom title
           root-desc=Custom description

    * `/mnt/cgitize`: map cgitize's output directory here.

Compose
-------

See the root docker-compose.yml file for a possible services definition.
In this configuration, cgitize pulls my repositories from GitHub every 3 hours.
You can test it by running

    docker-compose build
    docker-compose up -d

and visiting http://localhost:80/.
