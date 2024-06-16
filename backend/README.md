# Installation Guide for Local Server on Ubuntu:

## Setting up Mosquitto (MQTT Broker):
- **Ubuntu 22.04**
  - Install mosquitto and mosquitto-client:
    ```
    sudo apt install mosquitto mosquitto-client
    ```
  - Add the following lines to the file `/etc/mosquitto/mosquitto.conf`:
    ```
    allow_anonymous true  # Allow subscription/publishing without authentication
    listener 1883 0.0.0.0  # Use local machine's IP as the broker on port 1883
    ```

## Setting up Python 3.10 and Dependencies:
- **Python 3.10**

## Setting up PostgreSQL 14:
- **Initial Setup:**
- Access PostgreSQL in your terminal:
  ```
  sudo -u postgres psql
  ```
- Execute the following commands:
  ```
  CREATE DATABASE smartfarm;
  CREATE USER year3 WITH PASSWORD 'year3';
  GRANT ALL PRIVILEGES ON DATABASE smartfarm TO year3;
  ```
- Note: If you prefer different database, username, or password, ensure to update them in your code or `.env` file.


## Deploying on Local Network with Machine IP:
- **Make sure you in direcory .../server/backend**
- Navigate to `cd ./Year3_dev_Backend/main`
- **Install Virtual Environment:**
  ```
  python -m venv venv
  ```
- **Activate Virtual Environment:**
  ```
  source venv/bin/activate
  ```
- **Install Dependency Packages:**
  ```
  pip install -r requirements.txt
  ```
- **Make sure you in direcory .../server/backend**
- Navigate to `cd ./Year3_dev_Backend/main/Year3`
- **Apply Migrations to Database:**
  ```
  python manage.py makemigrations api
  python manage.py migrate
  ```
- **Run the Server on Specified IP (0.0.0.0) and Port (8000):**
  ```
  python manage.py runserver 0.0.0.0:8000
  ```

