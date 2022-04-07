"# exchangeproject"

Welcome to this project, a platform that simulates the basic operation of a bitcoin exchange

Tools used: Python(3.10.2), Django, MongoDB, Djongo

Requirements: MongoDB installed

Steps for run the project (Windows):

download the project

open the console inside the folder "exchangeproject-main"

- create a virtual environment -> "python -m venv myvenv"

- run the virtual environment -> "myvenv\Scripts\activate"

- install requirements.txt -> "pip install -r requirements.txt"

- "python manage.py makemigrations"

- "python manage.py migrate"

- "python manage.py makemigrations app"

- "python manage.py migrate app"

- run the project -> "python manage.py runserver"

populate the book order with default data -> go to "http://127.0.0.1:8000/createdata"
