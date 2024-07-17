How to run locally?

Step 1: Create a local postgres server on port 5432 or use a production database.

Step 2: Set credentials for the database in .env

    # Database environment
    DB_NAME=callerdev   # db name
    DB_USER=postgres    # db user
    DB_PASSWORD=        # db password
    DB_HOST=localhost   # db host
    DB_PORT=5432        # db port


Step 3: Create a virtual environment

    - cd calleridentity
    - python3 -m venv myvenv
    - myvenv\Scripts\activate  (Windows)
    - source myvenv/bin/activate (Linux)


Step 4: Install libraries from requirements.txt

    - pip install -r requirements.txt

Step 5: Start migration

    - python manage.py migrate

Step 6: Start Django server

    - python manage.py runserver

Alternatively, automated test cases can also be started using the following command:

    - python manage.py test


Step 7: Import Postman collection

Step 8: Ready for evaluation