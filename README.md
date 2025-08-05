## 📦 Requirements

- Python 3.8+
- Redis (running via Docker or locally)
- Django
- Django Channels
- Django REST Framework
- Channels Redis

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

docker run -p 6379:6379 -d redis

python manage.py migrate
python manage.py runserver

pip install daphne
daphne chatproject.asgi:application