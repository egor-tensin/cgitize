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
You can also set it to "minutely", "15min", "hourly", "daily", "weekly",
"monthly" or a custom 5-part cron schedule like "*/5 * * * *".

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

Here's an example docker-compose.yml file:

    version: '3'

    services:
      cgitize:
        environment:
          # Every 3 hours:
          SCHEDULE: '0 */3 * * *'
          # Set CGITIZE_{GITHUB,BITBUCKET,GITLAB}_{USERNAME,TOKEN} variables
          # here or in the config file.
        image: egortensin/cgitize:6
        restart: unless-stopped
        volumes:
          - ./example.toml:/etc/cgitize/cgitize.toml:ro
          - /srv/volumes/cgitize:/mnt/cgitize
      frontend:
        image: egortensin/cgitize-frontend:6
        ports:
          - '127.0.0.1:80:80'
        restart: unless-stopped
        volumes:
          - /srv/volumes/cgitize:/mnt/cgitize:ro

In this configuration, cgitize pulls repositories defined in example.toml every
3 hours and puts them to /srv/volumes/cgitize on the host.

To launch containers, run:

    docker-compose up -d

To inspect the repositories, visit http://localhost:80/.
