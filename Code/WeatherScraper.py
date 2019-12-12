from Code.Variables import *


def get_weather(city, kick_off, start_date):
    url = f"https://api.meteostat.net/v1/stations/search?q={city}&country=GB&key={API_KEY}"
    response = requests.request("GET", url)
    city_stations = json.loads(response.text)
    city_station = city_stations['data'][0]['id']

    url2 = f"https://api.meteostat.net/v1/history/hourly?station={city_station}&start={start_date}&end={start_date}&time_zone=Europe/London&time_format=Y-m-d%20H:i&key={API_KEY}"

    response = requests.request("GET", url2)
    station_weather = json.loads(response.text)
    kick_off_date = datetime.strptime(kick_off, "%H:%M")
    for weather_dict in station_weather['data']:
        time_local = datetime.strptime(weather_dict['time_local'].split()[1], "%H:%M")
        if time_local - kick_off_date >= timedelta(seconds=0):
            temperature = weather_dict['temperature']
            humidity = weather_dict['humidity']
            precipitation = weather_dict['precipitation']
            wind_speed = weather_dict['windspeed']
            break
    return [city, kick_off, temperature, humidity, precipitation, wind_speed]


class WeatherScraper:
    def __init__(self):
        conn = mysql.connector.connect(user=DB_USER, password=DB_PWD, host='localhost', database=DB_NAME)
        cur = conn.cursor()
        cur.execute("""SELECT web_id, stadium, kick_off, date 
        FROM match_results JOIN match_general_stats 
        ON match_results.web_id = match_general_stats.match_id
        """)
        result = cur.fetchall()
        for (web_id, stadium, kick_off, date) in result:
            city = stadium.split(", ")[-1].lower()
            start_date = dateparser.parse(date).strftime("%Y-%m-%d")
            print(date)
            try:
                weather = [web_id, date] + get_weather(city, kick_off, start_date)
            except IndexError:
                continue
            cur.execute("""INSERT IGNORE INTO match_weather 
            (match_id, date, city, kick_off, temperature, humidity, precipitation_mm, wind_speed_km_h) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", weather)
        conn.commit()
        cur.close()
        conn.close()
