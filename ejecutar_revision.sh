#!/bin/bash
# Ejecutar revisión de RSS (para cron los lunes 8h, 9h, 10h)
# Uso: ./ejecutar_revision.sh   o   bash ejecutar_revision.sh
cd "/Applications/Auto AAH RRSS"
[ -d venv ] && source venv/bin/activate
python main.py
