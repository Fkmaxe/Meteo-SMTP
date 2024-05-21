import requests
import schedule
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration de l'API OpenWeatherMap
API_KEY = ''
CITY = 'Angoulême,FR'
URL = f"http://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

# Configuration de l'email
EMAIL_ADDRESS = ''
EMAIL_PASSWORD = ''
RECIPIENT_EMAIL = ''
SMTP_SERVER = ''
SMTP_PORT = 587

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("Email envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")

def check_weather():
    response = requests.get(URL)
    data = response.json()

    if data['cod'] != '200':
        print("Erreur lors de la récupération des données météo.")
        return

    forecast_list = data['list']
    notifications = []

    for forecast in forecast_list[:5]:  # Limite aux 5 prochains jours
        date = datetime.utcfromtimestamp(forecast['dt'])
        temp = forecast['main']['temp']
        weather_description = forecast['weather'][0]['description']
        wind_speed = forecast['wind']['speed']
        cloudiness = forecast['clouds']['all']

        conditions_favorables = (temp >= 17 and temp <= 18 and
                                 'clear' in weather_description.lower() and
                                 wind_speed < 10 and cloudiness < 20)

        notification = f"Prévisions pour le {date.strftime('%Y-%m-%d %H:%M:%S')}:\n"
        notification += f"- Température: {temp}°C\n"
        notification += f"- Description: {weather_description}\n"
        notification += f"- Vitesse du vent: {wind_speed} m/s\n"
        notification += f"- Nébulosité: {cloudiness}%\n"

        if conditions_favorables:
            notification += "Conditions favorables pour un relevé de température.\n"
        else:
            notification += "Conditions non favorables pour un relevé de température.\n"

        notifications.append(notification)

    email_body = "\n\n".join(notifications)
    send_email("Prévisions Météo", email_body)

def test_email():
    subject = "Test d'envoi d'email"
    body = "Ceci est un email de test pour vérifier que la fonction d'envoi d'email fonctionne correctement."
    send_email(subject, body)

# Appeler la fonction de test pour envoyer un email au démarrage
test_email()

# Planifier la tâche une fois par jour
schedule.every().day.at("08:00").do(check_weather)

print("Bot de météo démarré...")
while True:
    schedule.run_pending()
    time.sleep(1)