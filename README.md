# Install requirements

## pip install

Follow this guide:
https://pip.pypa.io/en/stable/installation/

# Run the project
    docker-compose up --build

# Inside the docker console
    python manage.py makemigrations
    python manage.py migrate
    
# If not inside the docker console
    docker-compose exec webapp python manage.py makemigrations
    docker-compose exec webapp python manage.py migrate
    docker-compose exec webapp python manage.py createsuperuser

# Open the webapp on the following URL

    http://localhost:8000/
