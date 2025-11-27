#!/bin/sh

set -e

echo "Iniciando la aplicación Api Vixel.."

echo "Ejecutando migraciones de la base de datos..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "Aplicación Api Vixel preparada exitosamente.."

MODE=${1}
if [ "$MODE" = "production" ]; then
    echo "Iniciando en modo producción..."
    exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 
else 
    echo "Iniciando en modo desarrollo..."
    exec python manage.py runserver 0.0.0.0:8000
fi