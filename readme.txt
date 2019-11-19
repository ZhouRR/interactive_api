conda env create -f develop.yaml

source .bash_profile

conda deactivate
conda activate develop
cd ..

ps aux|grep 8098

PYTHONIOENCODING=utf-8 nohup python manage.py runserver 0.0.0.0:8098 >/dev/null 2>&1 &

django
djangorestframework
django-cors-headers
urllib3
channels
psycopg2
