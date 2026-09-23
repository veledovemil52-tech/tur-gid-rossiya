import os
import time
import uuid
import requests
import re
import urllib3
from dotenv import load_dotenv
from urllib.parse import quote_plus

# ============================================================
# ТУРГИД РОССИЯ 4.0
# Поиск городов + до 30 дней + длинные ответы + MAX API
# ============================================================

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = os.getenv("MAX_BOT_TOKEN")
GIGACHAT_AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

API_URL = "https://platform-api2.max.ru"

giga_token = None
giga_token_expires_at = 0

weather_cache = {}
WEATHER_CACHE_TIME = 600
map_geocode_cache = {}

user_sessions = {}

# MAX принимает максимум 4000 символов.
# Оставляем запас.
MAX_TEXT_LENGTH = 3800


if not TOKEN:
    raise RuntimeError("❌ Не найден MAX_BOT_TOKEN в .env")

if not GIGACHAT_AUTH_KEY:
    raise RuntimeError("❌ Не найден GIGACHAT_AUTH_KEY в .env")


# ============================================================
# КНОПКИ
# ============================================================

def button(text, payload):
    return {
        "text": text,
        "type": "message",
        "payload": payload
    }


def callback_button(text, payload):
    """Кнопка, которая не отправляет отдельное сообщение в чат."""
    return {
        "text": text,
        "type": "callback",
        "payload": payload
    }


def link_button(text, url):
    """Кнопка-ссылка: открывает карту напрямую, не отправляя сообщение в чат."""
    return {
        "text": text,
        "type": "link",
        "url": url
    }


def get_start_keyboard():
    return [
        [
            button("🔎 Найти город", "Найти город"),
            button("🏙️ Популярные города", "Популярные города")
        ]
    ]


def get_popular_cities_keyboard():
    cities = [
        "Москва",
        "Санкт-Петербург",
        "Казань",
        "Сочи",
        "Уфа",
        "Екатеринбург",
        "Краснодар",
        "Нижний Новгород",
        "Калининград",
        "Владивосток",
        "Новосибирск",
        "Ярославль"
    ]

    rows = []

    for i in range(0, len(cities), 2):
        rows.append([
            button(cities[i], cities[i]),
            button(cities[i + 1], cities[i + 1])
        ])

    rows.append([
        button("🔎 Найти другой город", "Найти город")
    ])

    return rows


def get_search_again_keyboard():
    return [
        [
            button("🔎 Новый поиск", "Найти город"),
            button("🏙️ Популярные", "Популярные города")
        ]
    ]


def get_companion_keyboard():
    return [
        [
            button("👤 Один", "Один"),
            button("👨‍👩‍👧 С семьёй", "С семьёй")
        ],
        [
            button("👩‍❤️‍👨 Вдвоём", "Вдвоём"),
            button("🎉 С друзьями", "С друзьями")
        ]
    ]


def get_days_keyboard():
    return [
        [
            button("1 день", "1 день"),
            button("2 дня", "2 дня"),
            button("3 дня", "3 дня")
        ],
        [
            button("4 дня", "4 дня"),
            button("5 дней", "5 дней"),
            button("7 дней", "7 дней")
        ],
        [
            button("10 дней", "10 дней"),
            button("14 дней", "14 дней"),
            button("21 день", "21 день")
        ],
        [
            button("30 дней", "30 дней"),
            button("✏️ Другое количество", "Другое количество")
        ]
    ]


def get_budget_keyboard():
    # Один понятный вариант: пользователь сам вводит бюджет.
    # Это избавляет интерфейс от повторяющихся бюджетных панелей.
    return [
        [button("✏️ Указать свой бюджет", "Свой бюджет")]
    ]


INTEREST_OPTIONS = [
    "🏛️ История и культура",
    "🌲 Природа",
    "🍽️ Еда и рестораны",
    "📸 Фото и красивые места",
    "🎭 Развлечения",
    "🏖️ Отдых и прогулки",
    "🛍️ Шопинг",
    "👨‍👩‍👧 Семейный отдых",
    "🏎️ Активный отдых",
    "🌙 Ночная жизнь"
]


def get_interests_keyboard(selected=None):
    """Надёжный мультивыбор через обычные message-кнопки.
    Бот редактирует одно и то же сообщение, поэтому чат не засыпает
    подтверждениями после каждого выбора.
    """
    selected = set(selected or [])
    rows = []
    for interest in INTEREST_OPTIONS:
        prefix = "✅ " if interest in selected else "⬜ "
        rows.append([button(prefix + interest, interest)])
    rows.append([button("🚀 Готово — продолжить", "Готово — продолжить")])
    return rows


def format_budget(budget):
    return budget or "Не указан"


def get_main_menu_buttons():
    return [
        [
            button("🗓️ Новый маршрут", "Составить новый маршрут"),
            button("🎲 Секретное место", "Секретное место")
        ],
        [
            button("📸 Инста-локации", "Инста-локации"),
            button("👨‍👩‍👧 С детьми", "С детьми")
        ],
        [
            button("💰 Бюджетно", "Бюджетно"),
            button("🏛 Достопримечательности", "Достопримечательности")
        ],
        [
            button("☕ Где поесть", "Где поесть"),
            button("🏨 Где остановиться", "Где остановиться")
        ],
        [
            button("🏙️ Другой город", "Выбрать другой город")
        ]
    ]


def geocode_route_place(city, place):
    """Ищет конкретную точку маршрута и возвращает (lat, lon).

    Для ссылок Яндекс.Карт используем координаты, а не названия мест:
    это намного надёжнее и соответствует официальному формату rtext.
    """
    cache_key = f"{city}|{place}".strip().lower()
    if cache_key in map_geocode_cache:
        return map_geocode_cache[cache_key]

    queries = [f"{place}, {city}, Россия", f"{place}, {city}"]

    for query in queries:
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 3,
                    "accept-language": "ru",
                    "countrycodes": "ru",
                },
                headers={"User-Agent": "TurGidRussia/5.2 (MAX bot)"},
                timeout=8,
            )
            response.raise_for_status()
            results = response.json() or []

            if results:
                # Предпочитаем результат внутри нужного города.
                city_lower = city.lower()
                chosen = next(
                    (
                        item for item in results
                        if city_lower in str(item.get("display_name", "")).lower()
                    ),
                    results[0],
                )
                point = (float(chosen["lat"]), float(chosen["lon"]))
                map_geocode_cache[cache_key] = point
                return point
        except (requests.RequestException, ValueError, KeyError, TypeError):
            continue

    map_geocode_cache[cache_key] = None
    return None


def build_yandex_route_url(city, route_text):
    """Строит рабочую ссылку Яндекс.Карт с реальными координатами точек.

    ВАЖНО: rtext Яндекс.Карт надёжно принимает координаты точек.
    Поэтому сначала извлекаем названия из маршрута, затем геокодируем их
    и только после этого формируем mode=routes&rtext=lat,lon~lat,lon...
    """
    import re

    places = []
    text = str(route_text or "")

    def add_place(value):
        value = str(value or "").strip()
        if not value:
            return

        value = re.sub(r"^\s*\d{1,2}:\d{2}\s*[—–-]\s*", "", value)
        value = re.sub(r"^[📍🟦🌦️🍽️🌙🚇💡🎯📸🕐]+\s*", "", value)
        value = re.split(r"\s+[—–-]\s+", value, maxsplit=1)[0].strip()
        value = re.split(r"\s*\.\s+(?=[А-ЯЁ])", value, maxsplit=1)[0].strip()
        value = re.sub(r"[.;,:]+$", "", value).strip()

        bad = {
            "маршрут", "погода", "передвижение", "где поесть",
            "где остановиться", "погода и запасной план", "вечерняя активность"
        }
        if value.lower() in bad:
            return
        if 2 <= len(value) <= 100 and value not in places:
            places.append(value)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        for match in re.findall(r"📍\s*([^\n]+)", line):
            add_place(match)

        if re.match(r"^\d{1,2}:\d{2}\s*[—–-]", line):
            candidate = re.sub(r"^\d{1,2}:\d{2}\s*[—–-]\s*", "", line)
            if not candidate.startswith(("🍽️", "🌙", "🌦️")):
                add_place(candidate)

    # Не больше 8 точек — Яндекс поддерживает до 8 дополнительных точек.
    places = places[:8]

    coordinates = []
    for place in places:
        point = geocode_route_place(city, place)
        if point:
            coordinates.append(point)

    if len(coordinates) >= 2:
        route_points = "~".join(
            f"{lat:.6f}%2C{lon:.6f}" for lat, lon in coordinates
        )
        return (
            "https://yandex.ru/maps/?mode=routes"
            f"&rtext={route_points}&rtt=auto"
        )

    # Если геокодировать удалось только одну/ни одной точки,
    # НЕ выдаём ложный маршрут. Открываем поиск по маршруту.
    query = f"{city} достопримечательности маршрут"
    return "https://yandex.ru/maps/?text=" + quote_plus(query)


def get_trip_actions_keyboard(days, map_url=None):
    """Действия после готового маршрута. Карта открывается напрямую по ссылке."""
    rows = [
        [button("🔄 Перестроить день", "Перестроить день"),
         button("🚫 Я уже был здесь", "Я уже был здесь")],
        [button("🕵️ Секретное место", "Секретное место"),
         button("📸 Места для фото", "Места для фото")],
    ]
    if map_url:
        rows.append([link_button("🗺️ Открыть маршрут на карте", map_url)])
    else:
        rows.append([button("🗺️ Маршрут на карте", "Маршрут на карте")])
    rows.append([button("🗓️ Новый маршрут", "Составить новый маршрут")])
    return rows


def get_route_ready_text(city, days):
    days_word = "день" if int(days) == 1 else "дня" if int(days) in (2, 3, 4) else "дней"
    return (
        f"✅ Маршрут готов!\n\n"
        f"🏙️ {city} · {days} {days_word}\n\n"
        "Выбирай, что сделать дальше:"
    )


def get_rebuild_day_keyboard(days):
    """Выбор дня для перестройки, максимум 30 дней."""
    rows = []
    current = []
    for day in range(1, int(days) + 1):
        current.append(button(f"{day}️⃣ День {day}", f"Перестроить день {day}"))
        if len(current) == 3:
            rows.append(current)
            current = []
    if current:
        rows.append(current)
    rows.append([button("⬅️ Назад к маршруту", "Назад к маршруту")])
    return rows


# ============================================================
# MAX API
# ============================================================
def edit_message(message_id, text=None, buttons=None, format="markdown"):
    """Редактирует сообщение бота через PUT /messages."""
    if not message_id:
        return False

    url = f"{API_URL}/messages"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    params = {"message_id": str(message_id)}
    payload = {}

    if text is not None:
        payload["text"] = str(text)
    if buttons is not None:
        payload["attachments"] = [] if not buttons else [{
            "type": "inline_keyboard",
            "payload": {"buttons": buttons}
        }]

    if format:
        payload["format"] = format

    try:
        response = requests.put(
            url, headers=headers, params=params, json=payload,
            timeout=20, verify=False
        )
        if response.status_code != 200:
            print(f"⚠️ Ошибка редактирования сообщения: {response.status_code} {response.text}")
            return False
        result = response.json() if response.content else {}
        if isinstance(result, dict) and result.get("success") is False:
            print(f"⚠️ MAX не изменил сообщение: {result}")
            return False
        return True
    except requests.RequestException as error:
        print(f"⚠️ Ошибка PUT /messages: {error}")
        return False



def get_updates(marker=None):
    url = f"{API_URL}/updates"

    headers = {
        "Authorization": TOKEN
    }

    params = {
        "limit": 100,
        "timeout": 30
    }

    if marker is not None:
        params["marker"] = marker

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=40,
            verify=False
        )

        if response.status_code == 200:
            return response.json()

        print(
            f"⚠️ Ошибка updates: "
            f"{response.status_code} {response.text}"
        )

    except requests.exceptions.Timeout:
        # Long Polling может ждать новое сообщение.
        # Это не означает, что бот сломался.
        return {}

    except requests.RequestException as error:
        print(f"⚠️ Ошибка подключения к MAX: {error}")

    return {}


def split_message(text, max_length=MAX_TEXT_LENGTH):
    """Разбивает длинный текст на части <= max_length."""
    text = str(text).strip()

    if len(text) <= max_length:
        return [text]

    parts = []
    remaining = text

    while len(remaining) > max_length:
        cut = remaining.rfind("\n\n", 0, max_length)

        if cut < 1000:
            cut = remaining.rfind("\n", 0, max_length)

        if cut < 1000:
            cut = remaining.rfind(" ", 0, max_length)

        if cut < 1000:
            cut = max_length

        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()

    if remaining:
        parts.append(remaining)

    return parts


def send_message(chat_id, text, buttons=None, return_message_id=False, format="markdown"):
    """Автоматически разбивает длинные сообщения."""
    url = f"{API_URL}/messages"

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    parts = split_message(text)

    last_message_id = None

    for index, part in enumerate(parts):
        params = {
            "chat_id": int(chat_id)
        }

        payload = {
            "text": part
        }

        if format:
            payload["format"] = format

        # Кнопки только на последнем сообщении.
        if buttons and index == len(parts) - 1:
            payload["attachments"] = [
                {
                    "type": "inline_keyboard",
                    "payload": {
                        "buttons": buttons
                    }
                }
            ]

        try:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=30,
                verify=False
            )

            if response.status_code not in (200, 201):
                print(
                    f"⚠️ Ошибка отправки: "
                    f"{response.status_code} {response.text}"
                )
                return False

            try:
                result = response.json()
                if isinstance(result, dict):
                    msg = result.get("message")
                    if isinstance(msg, dict):
                        last_message_id = msg.get("message_id") or msg.get("id")
                    last_message_id = last_message_id or result.get("message_id") or result.get("id")
            except Exception:
                pass

            print(f"🟢 Сообщение отправлено: chat_id={chat_id}")

            if len(parts) > 1:
                time.sleep(0.6)

        except requests.RequestException as error:
            print(f"⚠️ Ошибка отправки сообщения: {error}")
            return False

    return last_message_id if return_message_id else True


# ============================================================
# ПОИСК ГОРОДОВ
# ============================================================
# НОРМАЛИЗАЦИЯ ПОИСКОВОГО ЗАПРОСА
# ============================================================
def normalize_city_query(value):
    value = str(value or "").lower().replace("ё", "е")
    value = value.replace("-", " ")
    value = re.sub(r"[^0-9a-zа-я\s]", " ", value)
    return " ".join(value.split())


def search_cities(query):
    """Ищет города России. Точное совпадение возвращает сразу."""
    query = str(query or "").strip()
    normalized_query = normalize_city_query(query)

    if len(normalized_query) < 2:
        return []

    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote_plus(query)}"
        "&count=15"
        "&language=ru"
        "&format=json"
        "&countryCode=RU"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])
        cities = []

        for item in results:
            if item.get("country_code") != "RU":
                continue

            name = str(item.get("name", "")).strip()
            region = str(item.get("admin1", "")).strip()
            population = item.get("population")
            feature_code = str(item.get("feature_code", "")).upper()

            if not name:
                continue

            try:
                population = int(population) if population is not None else 0
            except (TypeError, ValueError):
                population = 0

            normalized_name = normalize_city_query(name)

            cities.append({
                "name": name,
                "region": region,
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "population": population,
                "feature_code": feature_code,
                "exact": normalized_name == normalized_query
            })

        # Сначала всегда проверяем точное название.
        exact = [city for city in cities if city["exact"]]
        if exact:
            exact.sort(key=lambda city: city["population"], reverse=True)
            return exact[:1]

        # Отсекаем мелкие населённые пункты и объекты без нормального
        # городского признака. Большие города идут первыми.
        filtered = []
        for city in cities:
            code = city["feature_code"]
            population = city["population"]

            is_city_type = (
                code in {"PPLC", "PPLA", "PPLA2", "PPLA3", "PPLA4"}
                or (code == "PPL" and population >= 1000)
            )

            if is_city_type:
                filtered.append(city)

        # Если API не дал feature_code, но есть население,
        # оставляем наиболее крупные варианты.
        if not filtered:
            filtered = [
                city for city in cities
                if city["population"] >= 1000
            ]

        unique = []
        seen = set()

        for city in sorted(
            filtered,
            key=lambda item: item["population"],
            reverse=True
        ):
            key = (
                normalize_city_query(city["name"]),
                normalize_city_query(city["region"])
            )

            if key not in seen:
                seen.add(key)
                unique.append(city)

        return unique[:8]

    except Exception as error:
        print(f"⚠️ Ошибка поиска города: {error}")
        return []



def select_city(chat_id, city):
    city = str(city or "").strip()
    if not city:
        return

    user_sessions[chat_id] = {
        "step": "WAITING_COMPANION",
        "city": city
    }

    send_message(
        chat_id,
        (
            f"**🏙️ Город выбран: {city}**\n\n"
            "👥 С кем ты отправляешься?"
        ),
        buttons=get_companion_keyboard()
    )

def city_display_name(city):
    name = city["name"]
    region = city.get("region", "")

    if region and region.lower() != name.lower():
        return f"{name} — {region}"

    return name


def get_city_search_keyboard(cities):
    rows = []

    for index, city in enumerate(cities):
        display = city_display_name(city)

        # Передаём индекс результата. Сам город хранится в сессии.
        rows.append([
            button(
                f"🏙️ {display}",
                f"ГОРОД_INDEX:{index}"
            )
        ])

    rows.append([
        button("🔎 Искать ещё", "Найти город"),
        button("🏙️ Популярные", "Популярные города")
    ])

    return rows


# ============================================================
# ПОГОДА
# ============================================================

def weather_description(code):
    descriptions = {
        0: "ясно ☀️",
        1: "преимущественно ясно 🌤️",
        2: "переменная облачность ⛅",
        3: "пасмурно ☁️",
        45: "туман 🌫️",
        48: "туман 🌫️",
        51: "слабая морось 🌦️",
        53: "морось 🌦️",
        55: "сильная морось 🌧️",
        61: "небольшой дождь 🌦️",
        63: "дождь 🌧️",
        65: "сильный дождь 🌧️",
        71: "небольшой снег 🌨️",
        73: "снег ❄️",
        75: "сильный снег ❄️",
        80: "ливневый дождь 🌧️",
        81: "ливни 🌧️",
        82: "сильные ливни ⛈️",
        95: "гроза ⛈️",
        96: "гроза с градом ⛈️",
        99: "сильная гроза с градом ⛈️",
    }
    return descriptions.get(code, "переменная погода 🌤️")


def get_weather_forecast(city_name, days=7):
    """Получает прогноз Open-Meteo и превращает его в данные для AI-маршрута.
    Максимум берём 16 дней — дальше точного прогноза нет.
    """
    city_key = city_name.lower().strip()
    forecast_days = min(max(int(days or 7), 1), 16)
    cache_key = f"{city_key}:{forecast_days}"

    cached = weather_cache.get(cache_key)
    if cached:
        timestamp, weather = cached
        if time.time() - timestamp < WEATHER_CACHE_TIME:
            return weather

    try:
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={quote_plus(city_name)}"
            "&count=1"
            "&language=ru"
            "&format=json"
        )

        geo_response = requests.get(geo_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        results = geo_data.get("results") or []

        if not results:
            return "Прогноз погоды для города не найден."

        location = results[0]
        latitude = location["latitude"]
        longitude = location["longitude"]

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&forecast_days={forecast_days}"
            "&timezone=auto"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code"
        )

        weather_response = requests.get(weather_url, timeout=10)
        weather_response.raise_for_status()
        data = weather_response.json()
        daily = data.get("daily", {})

        dates = daily.get("time", [])
        tmax = daily.get("temperature_2m_max", [])
        tmin = daily.get("temperature_2m_min", [])
        rain = daily.get("precipitation_probability_max", [])
        codes = daily.get("weather_code", [])

        if not dates:
            return "Прогноз погоды временно недоступен."

        lines = ["🌦️ ПРОГНОЗ ПОГОДЫ ДЛЯ МАРШРУТА"]

        for i, date in enumerate(dates):
            max_temp = round(tmax[i]) if i < len(tmax) and tmax[i] is not None else "—"
            min_temp = round(tmin[i]) if i < len(tmin) and tmin[i] is not None else "—"
            rain_prob = round(rain[i]) if i < len(rain) and rain[i] is not None else "—"
            code = int(codes[i]) if i < len(codes) and codes[i] is not None else 0
            condition = weather_description(code)

            lines.append(
                f"{i + 1}. {date}: {min_temp}…{max_temp}°C, "
                f"{condition}, вероятность осадков {rain_prob}%"
            )

        if int(days or 7) > 16:
            lines.append(
                "ℹ️ Точный прогноз доступен только на ближайшие 16 дней. "
                "Для остальных дней планируй универсальные варианты с учётом сезона."
            )

        result = "\n".join(lines)
        weather_cache[cache_key] = (time.time(), result)
        return result

    except Exception as error:
        print(f"⚠️ Ошибка получения прогноза: {error}")
        return "Прогноз погоды временно недоступен. Планируй маршрут с запасными вариантами."


def get_weather(city_name):
    """Короткая сводка для меню и дополнительных запросов."""
    forecast = get_weather_forecast(city_name, 1)
    if "1." in forecast:
        first_line = forecast.split("\n", 2)[-1]
        return first_line
    return forecast


def answer_callback(callback_id, text=None, buttons=None, format="markdown"):
    """Обновляет сообщение после callback-кнопки через POST /answers."""
    if not callback_id:
        return False

    url = f"{API_URL}/answers"
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    params = {"callback_id": str(callback_id)}
    payload = {}

    if text is not None or buttons is not None:
        message = {}
        if text is not None:
            message["text"] = text
        if buttons is not None:
            message["attachments"] = [{
                "type": "inline_keyboard",
                "payload": {"buttons": buttons}
            }]
        if format:
            message["format"] = format
        payload["message"] = message

    try:
        response = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=20,
            verify=False
        )
        if response.status_code not in (200, 201):
            print(f"⚠️ Ошибка callback: {response.status_code} {response.text}")
            return False
        return True
    except requests.RequestException as error:
        print(f"⚠️ Ошибка callback: {error}")
        return False


# ============================================================
# GIGACHAT
# ============================================================

def get_giga_token():
    global giga_token
    global giga_token_expires_at

    if giga_token and time.time() < giga_token_expires_at:
        return giga_token

    url = (
        "https://ngw.devices.sberbank.ru:9443"
        "/api/v2/oauth"
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}"
    }

    payload = {
        "scope": "GIGACHAT_API_PERS"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            verify=False,
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()

            giga_token = data.get("access_token")
            giga_token_expires_at = time.time() + 1500

            print("🟢 GigaChat токен получен")

            return giga_token

        print(
            f"⚠️ Ошибка получения GigaChat токена: "
            f"{response.status_code} {response.text}"
        )

    except requests.RequestException as error:
        print(f"⚠️ Ошибка GigaChat OAuth: {error}")

    return None


def get_ai_recommendation(prompt, city_name, search_term=""):
    token = get_giga_token()

    if not token:
        return (
            "📍 Не удалось подключиться к GigaChat.\n"
            "Попробуй немного позже."
        )

    url = (
        "https://gigachat.devices.sberbank.ru"
        "/api/v1/chat/completions"
    )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False,
            timeout=60
        )

        if response.status_code != 200:
            print(
                f"⚠️ GigaChat error: "
                f"{response.status_code} {response.text}"
            )

            return (
                f"📍 Не удалось сгенерировать "
                f"ответ для города {city_name}."
            )

        data = response.json()

        raw_text = (
            data["choices"][0]
            ["message"]["content"]
        )

        clean_text = (
            raw_text
            .replace("#", "")
            .replace("*", "")
            .strip()
        )

        query = city_name

        map_url = (
            "https://yandex.ru/maps/?text="
            + quote_plus(query)
        )

        return (
            f"{clean_text}\n\n"
            f"🗺️ Искать на карте:\n"
            f"{map_url}"
        )

    except Exception as error:
        print(f"⚠️ Ошибка GigaChat: {error}")

        return (
            f"📍 Не удалось сгенерировать "
            f"ответ для города {city_name}."
        )


# ============================================================
# PROMPTS
# ============================================================

def clean_ai_route_text(text):
    """Приводит ответ AI к аккуратному виду для MAX."""
    if not text:
        return text

    lines = []
    skip_table_separator = re.compile(
        r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$"
    )

    headings = {
        "🗓️ МАРШРУТ",
        "🍽️ ГДЕ ПОЕСТЬ",
        "🏨 ГДЕ ОСТАНОВИТЬСЯ",
        "🚇 ПЕРЕДВИЖЕНИЕ",
        "🌦️ ПОГОДА И ЗАПАСНОЙ ПЛАН",
    }

    for raw in str(text).replace("\r", "").split("\n"):
        line = raw.strip()

        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        line = line.replace("```markdown", "").replace("```", "")
        line = re.sub(r"^#{1,6}\s*", "", line)

        if skip_table_separator.match(line):
            continue

        if "|" in line:
            stripped = line.strip("|")
            cells = [c.strip() for c in stripped.split("|")]
            if len(cells) >= 2:
                line = " • ".join(c for c in cells if c)

        line = line.replace("---", "—")
        line = re.sub(r"[ \t]{2,}", " ", line)

        plain = line.replace("**", "").replace("__", "").strip()

        if plain in headings:
            line = f"**{plain}**"
        elif re.match(r"^(🟦\s*)?ДЕНЬ\s+\d+\s*[—–-]", plain, flags=re.I):
            line = f"**{plain}**"

        lines.append(line)

    out = "\n".join(lines).strip()
    out = re.sub(r"\n{3,}", "\n\n", out)

    out = re.sub(
        r"\n?🗺️\s*(Искать на карте|Карта города)\s*:\s*https?://[^\n]+",
        "",
        out,
        flags=re.I
    )
    out = re.sub(r"\n?https?://yandex\.ru/maps/[^\n]+", "", out, flags=re.I)

    return out.strip()

def build_master_prompt(city, companion, days, weather, budget="Не указан", interests=None):
    interests_text = ", ".join(interests or []) or "Без особых предпочтений"
    return f"""
Ты — профессиональный AI-гид по России. Составь красивый, практичный и персональный маршрут по городу {city}.

ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
Город: {city}
Компания: {companion}
Продолжительность: {days}
Бюджет на всю поездку: {budget}
Интересы: {interests_text}

ПРОГНОЗ
{weather}

ГЛАВНОЕ
1. Приоритет: интересы пользователя → бюджет → компания → погода.
2. Погода должна менять маршрут, а не просто описываться. Дождь/гроза — больше крытых мест; тепло и ясно — больше прогулок; холод — меньше долгих прогулок; жара — улица утром и вечером, помещения днём.
3. Не повторяй места.
4. Называй только реальные и хорошо известные достопримечательности, музеи, парки и другие локации.
5. Никогда не выдумывай названия кафе, ресторанов, отелей, музеев, улиц, островов, водопадов и других объектов.
6. Если не уверен, что конкретное место существует или находится в этом городе — не называй его. Лучше предложи известную реальную локацию или опиши тип места без выдуманного названия.
7. Не выдумывай цены, часы работы, события и другие точные факты, если они не даны во входных данных.
8. Используй данные прогноза только из блока ПРОГНОЗ и не придумывай другие погодные значения.
9. Не обещай точный прогноз дальше доступного горизонта.

ФОРМАТ ОТВЕТА — ОЧЕНЬ ВАЖНО
Используй Markdown только для оформления: названия разделов и строки «ДЕНЬ N» выделяй **жирным**.
Не используй таблицы, символ | и длинное вступление. Не добавляй отдельный раздел «почему этот вариант лучше».

🗓️ МАРШРУТ

🟦 ДЕНЬ 1 — короткое название
🌦️ Погода: кратко
09:00 — 📍 Место. Что делать. 1–2 ч.
11:30 — 📍 Место. Что делать. 1–2 ч.
14:00 — 🍽️ Обед: конкретный вариант или район.
15:30 — 📍 Место. Что делать.
18:30 — 📍 Место. Что делать.
20:30 — 🌙 Вечерняя активность.

Для каждого следующего дня используй такой же блок. Для короткой поездки давай 4–6 основных активностей в день. Для 8–30 дней — компактно, без огромных описаний.

🍽️ ГДЕ ПОЕСТЬ
3 конкретных варианта, подходящих под бюджет и интересы.

🏨 ГДЕ ОСТАНОВИТЬСЯ
2 варианта: бюджетный и комфортный.

🚇 ПЕРЕДВИЖЕНИЕ
Как удобнее перемещаться по городу и между точками.

🌦️ ПОГОДА И ЗАПАСНОЙ ПЛАН
Коротко: что делать, если погода ухудшится.

Не добавляй ссылки на карты — ссылку бот добавит сам.

Пиши так, чтобы ответ было приятно читать прямо в MAX: короткие блоки, понятные заголовки, эмодзи, без простыней текста.
""".strip()


def build_menu_prompt(city, weather, user_query):
    return f"""
Ты — профессиональный туристический гид по России.

Город: {city}
Погода: {weather}
Запрос пользователя: {user_query}

Дай конкретный и полезный ответ.

Правила:
- Используй эмодзи.
- Выделяй названия важных блоков **жирным**.
- Не используй таблицы и символ |.
- Если спрашивают места — называй конкретные места.
- Если спрашивают еду — называй конкретные кафе/рестораны.
- Если погода плохая — добавляй крытые варианты.
- Не пиши лишнюю воду.
- Ответ должен быть удобен для MAX.
""".strip()


# ============================================================
# UPDATE
# ============================================================

def extract_message(update):
    return (
        update.get("message")
        or update.get("body")
        or {}
    )


def extract_text(update, message):
    text = ""

    if isinstance(message.get("text"), str):
        text = message["text"]

    elif isinstance(message.get("body"), dict):
        text = message["body"].get("text", "")

    callback = update.get("callback")

    if isinstance(callback, dict):
        payload = callback.get("payload")

        if payload:
            text = payload

    message_payload = message.get("payload")

    if message_payload:
        text = message_payload

    return str(text).strip()


def ui_key(text):
    """Нормализует текст кнопок MAX: убирает эмодзи и лишние пробелы."""
    text = str(text or "")
    for token in [
        "🔎", "🏙️", "🏙", "👋", "🗓️", "🎲", "📸",
        "👨‍👩‍👧", "💰", "🏛️", "🏛", "☕", "🏨", "👤",
        "👩‍❤️‍👨", "🎉", "✏️", "✏", "📅", "👥", "🌤️", "🚀",
        "🌲", "🍽️", "📸", "🎭", "🏖️", "🛍️", "🏎️", "🌙", "⬜", "✅",
        "🔄", "🚫", "🕵️", "🗺️", "⬅️",
    ]:
        text = text.replace(token, "")
    text = text.replace("\ufe0f", "").replace("\u200d", "")
    return " ".join(text.split()).strip().lower()


def get_chat_id(message, update):
    recipient = message.get("recipient", {})

    return (
        recipient.get("chat_id")
        or message.get("chat_id")
        or update.get("chat_id")
    )



def send_welcome(chat_id):
    user_sessions[chat_id] = {
        "step": "WAITING_CITY",
        "city": None
    }

    send_message(
        chat_id,
        (
            "**👋 Добро пожаловать в «ТурГид Россия»!**\n\n"
            "Я помогу подобрать город, учесть твои интересы, "
            "бюджет и погоду и составить готовый маршрут.\n\n"
            "**🏙️ С чего начнём?**\n"
            "Нажми «Найти город» или выбери популярный вариант ниже."
        ),
        buttons=get_start_keyboard()
    )

# ============================================================
# ОБРАБОТКА СООБЩЕНИЯ
# ============================================================

def handle_update(update):
    update_type = update.get("update_type")

    if update_type == "bot_started":
        chat_id = update.get("chat_id")
        if chat_id:
            send_welcome(chat_id)
        return

    # Пользователь очистил диалог — начинаем заново.
    if update_type == "dialog_cleared":
        chat_id = update.get("chat_id")
        if chat_id:
            send_welcome(chat_id)
        return

    # Callback-кнопки оставляем поддержанными, но интересы используют
    # обычные message-кнопки — они надёжно приходят в message_created.
    if update.get("update_type") == "message_callback" or isinstance(update.get("callback"), dict):
        callback = update.get("callback") or {}
        print(f"ℹ️ Получен callback: {callback}")
        callback_id = callback.get("callback_id")
        if callback_id:
            answer_callback(callback_id)
        return

    message = extract_message(update)

    chat_id = get_chat_id(message, update)

    if not chat_id:
        print("⚠️ Не найден chat_id")
        return

    text = extract_text(update, message)
    clean_text = text.lower().strip()
    command = ui_key(text)

    if not clean_text:
        return

    print(
        f"\n📩 Запрос: {text} | command={command} | chat_id={chat_id}"
    )

    session = user_sessions.get(
        chat_id,
        {
            "step": "START",
            "city": None
        }
    )

    step = session.get("step", "START")


    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if (
        "привет" in clean_text
        or "/start" in clean_text
        or clean_text == "start"
    ):
        send_welcome(chat_id)
        return

    if step == "START":
        send_welcome(chat_id)
        return


    # --------------------------------------------------------
    # ПОПУЛЯРНЫЕ ГОРОДА
    # --------------------------------------------------------

    if command == "популярные города":
        user_sessions[chat_id] = {
            **session,
            "step": "WAITING_CITY"
        }

        send_message(
            chat_id,
            "🏙️ Выбери город:",
            buttons=get_popular_cities_keyboard()
        )
        return


    # --------------------------------------------------------
    # ПОИСК ГОРОДА
    # --------------------------------------------------------

    if (
        command == "найти город"
        or command == "найти другой город"
        or command == "выбрать другой город"
    ):
        user_sessions[chat_id] = {
            **session,
            "step": "SEARCH_CITY"
        }

        send_message(
            chat_id,
            (
                "🔎 Поиск города\n\n"
                "Напиши название города или хотя бы "
                "первые 2–3 буквы.\n\n"
                "Например:\n"
                "екат\n"
                "красн\n"
                "влад"
            ),
            buttons=get_popular_cities_keyboard()
        )
        return


    # --------------------------------------------------------
    # ВЫБОР ГОРОДА ИЗ ПОИСКА
    # --------------------------------------------------------

    # Кнопки выбора города могут прийти как payload,
    # так и как обычный текст кнопки. Учитываем оба варианта.
    selected_city = None

    # Новый надёжный способ — индекс сохранённого результата.
    if clean_text.startswith("город_index:"):
        try:
            index = int(text.split(":", 1)[1].strip())
            options = session.get("city_options", [])
            if 0 <= index < len(options):
                selected_city = str(options[index].get("name", "")).strip()
        except (ValueError, TypeError, IndexError):
            selected_city = None

    # Совместимость со старой версией.
    if not selected_city and clean_text.startswith("город:"):
        selected_city = text.split(":", 1)[1].strip()

    # Если MAX передал именно текст кнопки: 
    # "🏙️ Волгоград — Волгоградская Область".
    if not selected_city and step == "SEARCH_RESULTS":
        options = session.get("city_options", [])
        key = ui_key(text)
        for item in options:
            name = str(item.get("name", "")).strip()
            region = str(item.get("region", "")).strip()
            display = (
                f"{name} — {region}"
                if region and region.lower() != name.lower()
                else name
            )
            if key in {ui_key(name), ui_key(display)}:
                selected_city = name
                break

    if selected_city:
        select_city(chat_id, selected_city)
        return


    # --------------------------------------------------------
    # ПОПУЛЯРНЫЙ ГОРОД
    # --------------------------------------------------------

    popular_cities = {
        "москва",
        "санкт-петербург",
        "казань",
        "сочи",
        "уфа",
        "екатеринбург",
        "краснодар",
        "нижний новгород",
        "калининград",
        "владивосток",
        "новосибирск",
        "ярославль"
    }

    if (
        step == "WAITING_CITY"
        and command in popular_cities
    ):
        select_city(chat_id, text.strip())
        return


    # --------------------------------------------------------
    # ПОИСК: ПОЛЬЗОВАТЕЛЬ ПИШЕТ БУКВЫ
    # --------------------------------------------------------

    if step == "SEARCH_CITY":
        results = search_cities(text)

        if not results:
            send_message(
                chat_id,
                (
                    "😕 **Не нашёл подходящий город.**\n\n"
                    "Напиши полное название или первые 2–3 буквы.\n"
                    "Например: Москва, екат, красн."
                ),
                buttons=get_search_again_keyboard()
            )
            return

        # Точное название города — сразу переходим дальше.
        if (
            len(results) == 1
            and normalize_city_query(results[0]["name"])
            == normalize_city_query(text)
        ):
            select_city(chat_id, results[0]["name"])
            return

        user_sessions[chat_id] = {
            **session,
            "step": "SEARCH_RESULTS",
            "city_options": results
        }

        send_message(
            chat_id,
            (
                f"🔎 **Нашёл вариантов: {len(results)}**\n\n"
                "Выбери нужный город:"
            ),
            buttons=get_city_search_keyboard(results)
        )
        return


    # --------------------------------------------------------
    # ПОЛЬЗОВАТЕЛЬ ПИШЕТ НОВЫЙ ЗАПРОС ПОСЛЕ РЕЗУЛЬТАТОВ
    # --------------------------------------------------------

    if step == "SEARCH_RESULTS":
        results = search_cities(text)

        if (
            len(results) == 1
            and normalize_city_query(results[0]["name"])
            == normalize_city_query(text)
        ):
            select_city(chat_id, results[0]["name"])
            return

        if results:
            user_sessions[chat_id] = {
                **session,
                "step": "SEARCH_RESULTS",
                "city_options": results
            }
            send_message(
                chat_id,
                "🔎 **Выбери город из результатов:**",
                buttons=get_city_search_keyboard(results)
            )
        else:
            send_message(
                chat_id,
                "😕 **Не нашёл подходящий город.** Попробуй другие буквы.",
                buttons=get_search_again_keyboard()
            )
        return


    # --------------------------------------------------------
    # ГОРОД НАПРЯМУЮ
    # --------------------------------------------------------

    if step == "WAITING_CITY":
        results = search_cities(text)

        if not results:
            send_message(
                chat_id,
                (
                    "😕 **Не нашёл такой город.**\n\n"
                    "Попробуй ещё раз или используй поиск."
                ),
                buttons=get_search_again_keyboard()
            )
            return

        # Полное название города — сразу к следующему шагу.
        if (
            len(results) == 1
            and normalize_city_query(results[0]["name"])
            == normalize_city_query(text)
        ):
            select_city(chat_id, results[0]["name"])
            return

        user_sessions[chat_id] = {
            **session,
            "step": "SEARCH_RESULTS",
            "city_options": results
        }

        send_message(
            chat_id,
            "🔎 **Выбери нужный город:**",
            buttons=get_city_search_keyboard(results)
        )
        return


    # --------------------------------------------------------
    # КОМПАНИЯ
    # --------------------------------------------------------

    if step == "WAITING_COMPANION":
        companion = text.strip()

        user_sessions[chat_id] = {
            **session,
            "step": "WAITING_DAYS",
            "companion": companion
        }

        send_message(
            chat_id,
            (
                f"**👥 Отлично: {companion}**\n\n"
                "📅 На сколько дней планируешь поездку?\n\n"
                "Можно выбрать вариант ниже "
                "или написать своё количество дней."
            ),
            buttons=get_days_keyboard()
        )
        return


    # --------------------------------------------------------
    # ДНИ
    # --------------------------------------------------------

    if step == "WAITING_DAYS":

        if command == "другое количество":
            user_sessions[chat_id] = {
                **session,
                "step": "WAITING_CUSTOM_DAYS"
            }

            send_message(
                chat_id,
                (
                    "✏️ Напиши количество дней числом.\n\n"
                    "Например: 6, 12 или 20.\n"
                    "Максимум — 30 дней."
                )
            )
            return

        digits = "".join(
            ch for ch in clean_text
            if ch.isdigit()
        )

        if not digits:
            send_message(
                chat_id,
                "📅 Напиши количество дней от 1 до 30.",
                buttons=get_days_keyboard()
            )
            return

        days_number = int(digits)

        if not 1 <= days_number <= 30:
            send_message(
                chat_id,
                "📅 Количество дней должно быть от 1 до 30.",
                buttons=get_days_keyboard()
            )
            return

        updated_session = {
            **session,
            "step": "WAITING_BUDGET",
            "days": days_number
        }
        user_sessions[chat_id] = updated_session

        budget_message_id = send_message(
            chat_id,
            "💸 Отлично! Теперь укажи бюджет на всю поездку.\n\n"
            "Нажми кнопку и введи сумму в рублях.",
            buttons=get_budget_keyboard(),
            return_message_id=True
        )
        user_sessions[chat_id]["budget_message_id"] = budget_message_id
        return


    # --------------------------------------------------------
    # СВОЁ КОЛИЧЕСТВО ДНЕЙ
    # --------------------------------------------------------

    if step == "WAITING_CUSTOM_DAYS":
        digits = "".join(
            ch for ch in clean_text
            if ch.isdigit()
        )

        if not digits:
            send_message(
                chat_id,
                "✏️ Напиши число от 1 до 30."
            )
            return

        days_number = int(digits)

        if not 1 <= days_number <= 30:
            send_message(
                chat_id,
                "📅 Можно выбрать от 1 до 30 дней."
            )
            return

        updated_session = {
            **session,
            "step": "WAITING_BUDGET",
            "days": days_number
        }
        user_sessions[chat_id] = updated_session

        budget_message_id = send_message(
            chat_id,
            "💸 Теперь укажи бюджет на всю поездку.",
            buttons=get_budget_keyboard(),
            return_message_id=True
        )
        user_sessions[chat_id]["budget_message_id"] = budget_message_id
        return


    # --------------------------------------------------------
    # БЮДЖЕТ
    # --------------------------------------------------------

    if step == "WAITING_BUDGET":
        # Теперь здесь только одна кнопка. После неё пользователь
        # вводит сумму сам — без диапазонов и без дублирования панели.
        if command in {"свой бюджет", "указать свой бюджет", "бюджет"}:
            user_sessions[chat_id] = {
                **session,
                "step": "WAITING_CUSTOM_BUDGET"
            }
            budget_message_id = session.get("budget_message_id")
            if budget_message_id:
                edit_message(
                    budget_message_id,
                    "✏️ Укажи бюджет на всю поездку в рублях.\n\n"
                    "Например: 25000",
                    []
                )
            else:
                send_message(
                    chat_id,
                    "✏️ Укажи бюджет на всю поездку в рублях.\n\n"
                    "Например: 25000"
                )
            return

        # На случай, если пользователь сразу написал сумму.
        digits = "".join(ch for ch in text if ch.isdigit())
        if digits:
            amount = int(digits)
            if 1000 <= amount <= 10000000:
                budget = f"{amount:,}".replace(",", " ") + " ₽"
                user_sessions[chat_id] = {
                    **session,
                    "step": "WAITING_INTERESTS",
                    "budget": budget,
                    "interests": []
                }
                interest_message_id = send_message(
                    chat_id,
                    f"**💸 Бюджет: {budget}**\n\n**🎯 Выбери интересы для поездки**\n\nМожно выбрать несколько пунктов.\nПосле каждого выбора нажимай следующий.\nКогда всё выбрал — **🚀 Готово**.",
                    buttons=get_interests_keyboard([]),
                    return_message_id=True
                )
                user_sessions[chat_id]["interest_message_id"] = interest_message_id
                return

        send_message(
            chat_id,
            "✏️ Нажми «Указать свой бюджет», затем введи сумму в рублях.",
            buttons=get_budget_keyboard()
        )
        return


    # --------------------------------------------------------
    # СВОЙ БЮДЖЕТ
    # --------------------------------------------------------

    if step == "WAITING_CUSTOM_BUDGET":
        digits = "".join(ch for ch in clean_text if ch.isdigit())
        if not digits:
            send_message(chat_id, "✏️ Напиши бюджет числом, например 15000.")
            return

        amount = int(digits)
        if amount < 1000 or amount > 10000000:
            send_message(chat_id, "💸 Укажи бюджет от 1 000 до 10 000 000 ₽.")
            return

        budget = f"{amount:,}".replace(",", " ") + " ₽"
        user_sessions[chat_id] = {
            **session,
            "step": "WAITING_INTERESTS",
            "budget": budget,
            "interests": []
        }
        interest_message_id = send_message(
            chat_id,
            f"**💸 Бюджет: {budget}**\n\n**🎯 Выбери интересы для поездки**\n\nМожно выбрать несколько пунктов.\nПосле каждого выбора нажимай следующий.\nКогда всё выбрал — **🚀 Готово**.",
            buttons=get_interests_keyboard([]),
            return_message_id=True
        )
        user_sessions[chat_id]["interest_message_id"] = interest_message_id
        return


    # --------------------------------------------------------
    # ИНТЕРЕСЫ
    # --------------------------------------------------------

    if step == "WAITING_INTERESTS":
        interests = list(session.get("interests", []))

        if command == "готово" or command.startswith("готово — продолжить") or command.startswith("готово - продолжить"):
            if not interests:
                interests = ["🌟 Разнообразная программа"]
            updated_session = {
                **session,
                "step": "GENERATING",
                "interests": interests
            }
            user_sessions[chat_id] = updated_session

            # Убираем клавиатуру из единственного сообщения с выбором.
            interest_message_id = session.get("interest_message_id")
            if interest_message_id:
                edit_message(
                    interest_message_id,
                    "**🚀 Готово!** Начинаю составлять персональный маршрут...",
                    []
                )

            start_trip(chat_id, updated_session, int(updated_session.get("days", 1)))
            return

        matched = None
        for interest in INTEREST_OPTIONS:
            if command == ui_key(interest) or command == ui_key("⬜ " + interest) or command == ui_key("✅ " + interest):
                matched = interest
                break

        if matched:
            if matched in interests:
                interests.remove(matched)
            else:
                interests.append(matched)

            interest_message_id = session.get("interest_message_id")
            user_sessions[chat_id] = {
                **session,
                "step": "WAITING_INTERESTS",
                "interests": interests
            }

            # Ничего нового в чат не отправляем — просто меняем существующее
            # сообщение с кнопками.
            if interest_message_id:
                selected_text = ", ".join(interests) if interests else "пока ничего"
                edit_message(
                    interest_message_id,
                    f"**🎯 Выбрано: {len(interests)}**\n{selected_text}\n\n➕ **Можно выбрать ещё** — просто нажимай следующие пункты.\nКогда закончишь — **🚀 Готово**.",
                    get_interests_keyboard(interests)
                )
            return

        return


    # --------------------------------------------------------
    # ДЕЙСТВИЯ ПОСЛЕ ГОТОВОГО МАРШРУТА
    # --------------------------------------------------------

    if command == "перестроить день":
        days = int(session.get("days", 1) or 1)
        user_sessions[chat_id] = {**session, "step": "WAITING_REBUILD_DAY"}
        send_message(
            chat_id,
            "🔄 Какой день перестроить?\n\n"
            "Я сохраню город, бюджет, интересы, компанию и учту погоду.",
            buttons=get_rebuild_day_keyboard(days)
        )
        return

    if step == "WAITING_REBUILD_DAY":
        if command == "назад к маршруту":
            user_sessions[chat_id] = {**session, "step": "MAIN_MENU"}
            send_message(
                chat_id,
                "🗓️ Возвращаемся к действиям маршрута.",
                buttons=get_trip_actions_keyboard(int(session.get("days", 1) or 1))
            )
            return

        import re
        day_number = None
        m = re.search(r"перестроить день\s*(\d+)", command)
        if m:
            day_number = int(m.group(1))
        else:
            m = re.search(r"день\s*(\d+)", command)
            if m:
                day_number = int(m.group(1))

        total_days = int(session.get("days", 1) or 1)
        if not day_number or not (1 <= day_number <= total_days):
            send_message(chat_id, "🔄 Выбери день кнопкой ниже.", buttons=get_rebuild_day_keyboard(total_days))
            return

        city = session.get("city") or "Москва"
        companion = session.get("companion", "Один")
        budget = session.get("budget", "Не указан")
        interests = session.get("interests", [])
        weather = session.get("weather", "") or get_weather_forecast(city, total_days)
        route_text = session.get("route_text", "")

        user_sessions[chat_id] = {**session, "step": "GENERATING_REBUILD"}
        send_message(
            chat_id,
            f"🔄 Перестраиваю день {day_number}...\n\n"
            "🧠 Сохраняю твои предпочтения и ищу другой вариант."
        )

        rebuild_prompt = f"""
Ты — профессиональный AI-гид по России.

Город: {city}
Компания: {companion}
Продолжительность поездки: {total_days} дней
Бюджет: {budget}
Интересы: {', '.join(interests) if interests else 'без особых предпочтений'}
Погода на поездку:
{weather}

Исходный маршрут пользователя:
{route_text[:14000]}

Пользователь хочет полностью заменить ТОЛЬКО день {day_number}.

Сделай новый вариант дня {day_number}, не повторяя ключевые места и активности из исходного дня.
Обязательно учитывай бюджет, интересы, компанию и прогноз погоды именно для этого дня.
Если дождь — больше крытых мест; если хорошая погода — больше прогулок; если жара или холод — адаптируй расписание.

Формат:
🔄 НОВЫЙ ВАРИАНТ — ДЕНЬ {day_number}

09:00 — ...
...
21:00 — ...

Не добавляй раздел «почему этот вариант лучше».

Не выдумывай точные цены и часы работы, если не уверен.
Не используй # и *.
""".strip()

        ai_response = get_ai_recommendation(rebuild_prompt, city)
        user_sessions[chat_id] = {
            **session,
            "step": "MAIN_MENU",
            "weather": weather,
            "last_rebuilt_day": day_number
        }
        rebuilt_text = clean_ai_route_text(ai_response)
        map_url = build_yandex_route_url(city, rebuilt_text)
        user_sessions[chat_id]["map_url"] = map_url
        send_message(chat_id, rebuilt_text)
        send_message(
            chat_id,
            "**✅ Новый вариант дня готов!**\n\n"
            "Выбирай следующее действие:",
            buttons=get_trip_actions_keyboard(total_days, map_url=map_url)
        )
        return

    if command == "я уже был здесь":
        user_sessions[chat_id] = {**session, "step": "WAITING_VISITED_PLACE"}
        send_message(
            chat_id,
            "🚫 Напиши название места, которое уже посещал.\n\n"
            "Например: Красная площадь"
        )
        return

    if step == "WAITING_VISITED_PLACE":
        visited = text.strip()
        if len(visited) < 2:
            send_message(chat_id, "🚫 Напиши название места, например: Эрмитаж.")
            return

        city = session.get("city") or "Москва"
        companion = session.get("companion", "Один")
        budget = session.get("budget", "Не указан")
        interests = session.get("interests", [])
        days = int(session.get("days", 1) or 1)
        weather = session.get("weather", "") or get_weather_forecast(city, days)
        route_text = session.get("route_text", "")

        send_message(chat_id, "🚫 Понял. Убираю это место и подбираю замену...")
        visited_prompt = f"""
Ты — профессиональный AI-гид по России.
Город: {city}
Компания: {companion}
Дней: {days}
Бюджет: {budget}
Интересы: {', '.join(interests) if interests else 'без особых предпочтений'}
Погода:
{weather}

Исходный маршрут:
{route_text[:14000]}

Пользователь уже был в месте: {visited}

Предложи реальную замену этому месту. Не предлагай само это место и не повторяй его очевидные дубликаты.
Сохрани общий стиль поездки и учти бюджет, интересы, компанию и погоду.
Дай конкретное место, чем заняться и как встроить замену в маршрут.
Не выдумывай точные цены и часы работы.
""".strip()
        ai_response = get_ai_recommendation(visited_prompt, city, search_term=f"{visited} {city}")
        user_sessions[chat_id] = {**session, "step": "MAIN_MENU", "weather": weather, "last_visited": visited}
        send_message(chat_id, ai_response, buttons=get_trip_actions_keyboard(days))
        return

    if command == "секретное место":
        city = session.get("city") or "Москва"
        interests = session.get("interests", [])
        budget = session.get("budget", "Не указан")
        companion = session.get("companion", "Один")
        secret_prompt = f"""
Ты — AI-гид по России.
Город: {city}
Компания: {companion}
Бюджет: {budget}
Интересы: {', '.join(interests) if interests else 'без особых предпочтений'}

Подбери одно необычное, но реальное место в городе, которое может понравиться туристу и не является самой очевидной достопримечательностью.
Не выдумывай место. Если не уверен в существовании конкретного места, предложи известную, но менее туристическую локацию.
Ответ: название, почему интересно, что там делать и примерный формат расходов без выдуманных точных цен.
""".strip()
        send_message(chat_id, "🕵️ Ищу секретное место...")
        ai_response = get_ai_recommendation(secret_prompt, city, search_term=f"необычное место {city}")
        send_message(chat_id, ai_response, buttons=get_trip_actions_keyboard(int(session.get("days", 1) or 1)))
        return

    if command == "места для фото" or command == "инста-локации":
        city = session.get("city") or "Москва"
        photo_prompt = f"""
Ты — AI-гид по России. Город: {city}.
Подбери 5 реальных красивых мест для фотографий.
Для каждого: 📍 место, 📸 что лучше фотографировать, 🕐 лучшее время, 💡 короткий совет.
Не выдумывай места. Не используй # и *.
""".strip()
        send_message(chat_id, "📸 Подбираю фототочки...")
        ai_response = get_ai_recommendation(photo_prompt, city, search_term=f"фотографии {city}")
        send_message(chat_id, ai_response, buttons=get_trip_actions_keyboard(int(session.get("days", 1) or 1)))
        return

    if command == "маршрут на карте":
        city = session.get("city") or "Москва"
        map_url = session.get("map_url") or build_yandex_route_url(city, session.get("route_text", ""))
        user_sessions[chat_id] = {**session, "map_url": map_url, "step": "MAIN_MENU"}
        send_message(
            chat_id,
            "🗺️ Маршрут готов — нажми кнопку ниже, чтобы открыть его в Яндекс Картах.",
            buttons=get_trip_actions_keyboard(int(session.get("days", 1) or 1), map_url=map_url)
        )
        return

    # --------------------------------------------------------
    # НОВЫЙ МАРШРУТ
    # --------------------------------------------------------

    if command == "составить новый маршрут":
        user_sessions[chat_id] = {
            "step": "SEARCH_CITY",
            "city": session.get("city")
        }

        send_message(
            chat_id,
            (
                "🗓️ Отлично! Начнём новый маршрут.\n\n"
                "Напиши город или первые буквы:"
            ),
            buttons=get_popular_cities_keyboard()
        )
        return


    # --------------------------------------------------------
    # ГЛАВНОЕ МЕНЮ
    # --------------------------------------------------------

    city = session.get("city") or "Москва"
    weather = get_weather(city)

    prompt = build_menu_prompt(
        city,
        weather,
        text
    )

    ai_response = get_ai_recommendation(
        prompt,
        city,
        search_term=f"{text} {city}"
    )

    send_message(
        chat_id,
        ai_response,
        buttons=get_main_menu_buttons()
    )


# ============================================================
# СОЗДАНИЕ МАРШРУТА
# ============================================================

def start_trip(chat_id, session, days_number, send_status=True):
    city = session.get("city") or "Москва"
    companion = session.get("companion", "Один")
    budget = session.get("budget", "Не указан")
    interests = session.get("interests", [])

    days_text = (
        "1 день"
        if days_number == 1
        else f"{days_number} дней"
    )

    user_sessions[chat_id] = {
        "step": "GENERATING",
        "city": city,
        "companion": companion,
        "days": days_number,
        "budget": budget,
        "interests": interests
    }

    if send_status:
        send_message(
            chat_id,
            (
                "🧠 Составляю персональную поездку...\n\n"
                f"🏙️ {city}\n"
                f"👥 {companion}\n"
                f"📅 {days_text}\n"
                f"💸 {budget}\n"
                f"🎯 {', '.join(interests) if interests else 'Без особых предпочтений'}\n\n"
                "⏳ Это может занять немного времени."
            )
        )

    weather = get_weather_forecast(city, days_number)

    prompt = build_master_prompt(
        city,
        companion,
        days_text,
        weather,
        budget,
        interests
    )

    ai_response = get_ai_recommendation(
        prompt,
        city
    )

    user_sessions[chat_id] = {
        "step": "MAIN_MENU",
        "city": city,
        "companion": companion,
        "days": days_number,
        "budget": budget,
        "interests": interests,
        "weather": weather,
        "route_text": ai_response
    }

    cleaned_route = clean_ai_route_text(ai_response)
    map_url = build_yandex_route_url(city, cleaned_route)
    user_sessions[chat_id]["map_url"] = map_url

    # Важно: отправляем маршрут и нижнюю панель одним вызовом.
    # Если маршрут длиннее лимита MAX, send_message сам разобьёт его
    # на части и прикрепит кнопки только к последней части.
    # Это также исключает ситуацию, когда второй POST /messages
    # попадает под ограничение MAX в 2 сообщения/секунду.
    final_text = (
        cleaned_route.rstrip()
        + "\n\n—\n\n"
        + get_route_ready_text(city, days_number)
    )
    send_message(
        chat_id,
        final_text,
        buttons=get_trip_actions_keyboard(days_number, map_url=map_url)
    )


# ============================================================
# ЗАПУСК
# ============================================================

def main():
    print("🚀 ТурГид Россия 5.4 запущен!")
    print("🔎 Поиск городов: включён")
    print("📅 Дни: 1–30 + своё значение")
    print("✂️ Разбиение длинных сообщений: включено")
    print("🔄 Перестройка дня: включена")
    print("✨ Полированный интерфейс: включён")
    print("⏳ Long Polling MAX: включён")
    print("")

    marker = None

    while True:
        try:
            data = get_updates(marker)

            if not isinstance(data, dict):
                time.sleep(1)
                continue

            updates = data.get("updates") or []

            for update in updates:
                try:
                    handle_update(update)
                except Exception as error:
                    print(
                        f"🔥 Ошибка обработки update: {error}"
                    )

            new_marker = data.get("marker")

            if new_marker is not None:
                marker = new_marker

        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен.")
            break

        except Exception as error:
            print(
                f"🔥 Критическая ошибка: {error}"
            )
            time.sleep(2)


if __name__ == "__main__":
    main()
