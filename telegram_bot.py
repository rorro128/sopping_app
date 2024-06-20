import logging
import sqlite3
import pytesseract
import re
import pandas as pd
from dotenv import load_dotenv
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

# Configura el logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token de Telegram del archivo .env
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Ruta a tesseract.exe en Windows

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('¡Hola! Envíame una tarea para agendar.')

def add_task(update: Update, context: CallbackContext) -> None:
    task = ' '.join(context.args)
    date = '2024-06-18'  # Puedes cambiar esto para obtener la fecha de los mensajes

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", (task, date))
    conn.commit()
    conn.close()

    update.message.reply_text(f'Tarea "{task}" agendada para {date}.')

def get_tasks(update: Update, context: CallbackContext) -> None:
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()

    if tasks:
        tasks_str = '\n'.join([f"{task[1]} - {task[2]}" for task in tasks])
        update.message.reply_text(tasks_str)
    else:
        update.message.reply_text('No hay tareas agendadas.')

def extract_data_from_image(image_path):
    resultados = []
    text = pytesseract.image_to_string(Image.open(image_path))
    fecha_regex = r'\b\d{2}-\d{2}-\d{4}\b'
    importe_regex = r'TOTAL\s+\$\d{1,3}(?:\.\d{3})*'
    productos_regex = r'\b780\d{10}\b'
    fecha_match = str(re.search(fecha_regex, text))
    importe_match = str(re.findall(importe_regex, text)[1])
    productos = str(len(re.findall(productos_regex, text)))

    resultados.extend([fecha_match, importe_match, productos])
    print(resultados)

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute("INSERT INTO shopping (date, date, quantity) VALUES (?, ?, ?)", (fecha_match, importe_match, productos))
    conn.commit()
    conn.close()

    #df = pd.DataFrame(resultados, columns=["Fecha", "Importe", "Productos"])
    #print(df)
    # Aquí puedes procesar el texto extraído para obtener los datos específicos de la boleta
    return resultados

def handle_photo(update: Update, context: CallbackContext) -> None:
    file = update.message.photo[-1].get_file()
    image_path = 'downloaded_photo.jpg'
    file.download(image_path)

    extracted_text = extract_data_from_image(image_path)
    os.remove(image_path)  # Eliminar la imagen descargada después del procesamiento

    update.message.reply_text(f'Datos extraídos de la boleta:\n{extracted_text}')

def main() -> None:
    # Crea el Updater y pasa tu token
    updater = Updater(TOKEN, use_context=True)

    # Obtén el dispatcher para registrar los handlers
    dp = updater.dispatcher

    # Comandos
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('add', add_task))
    dp.add_handler(CommandHandler('tasks', get_tasks))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    # Inicia el Bot
    updater.start_polling()

    # Corre el bot hasta que se presione Ctrl-C o el proceso reciba SIGINT, SIGTERM o SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()