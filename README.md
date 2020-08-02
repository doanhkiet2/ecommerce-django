"# ecommerce-django" 
python -m vene venv
venv/scripts/active.bat(venv/bin/activate)
pip install -r requirements.txt
python manager.py migrate
python manager.py runserver
