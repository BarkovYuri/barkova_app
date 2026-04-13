cd ~/Dev/doctor-app/backend                            
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


cd ~/Dev/doctor-app/frontend                           
npm run dev   