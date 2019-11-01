conda env create -f xiaobeibot.yaml

conda deactivate
conda activate xiaobeibot
cd ..
PYTHONIOENCODING=utf-8 python manage.py runserver 0.0.0.0:8098 > message.log &
