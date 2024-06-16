# HOW TO RUN WEB APPLICATION

## Install Docker version 25.0.3 in Ubuntu

### Set up Docker's apt repository.:
- Before you install Docker Engine for the first time on a new host machine, you need to set up the Docker repository. Afterward, you can install and update Docker from the repository.
    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt-get update
    ```
### Install the Docker packages.
- To install the latest version, run:
    ```bash
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```
## Run Application
- Navigate to the directory .../server
- Run the following commands:
    ```bash
    cd .\backend\Year3_dev_Backend\main\Year3\
    chmod +x .\entrypoint.sh
    sudo docker compose up -d --build
    ```

## Backup Database
- Navigate to the directory .../server
- Copy the backup file `backup_db.sql` to the `database` container:
    ```bash
    sudo docker cp ./backup_db.sql database:/tmp/backup_db.sql
    ```
- Access the shell of the `database` container:
    ```bash
    sudo docker exec -it database bash
    ```
- Access the PostgreSQL command line interface:
    ```bash
    psql -U year3 -d smartfarm
    ```
- Execute the following commands in the PostgreSQL shell:
    ```sql
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    exit
    ```
- Change directory to `/tmp`:
    ```bash
    cd tmp
    ```
- Restore the database from the backup file:
    ```bash
    psql -U year3 -d smartfarm -f backup_db.sql
    ```
