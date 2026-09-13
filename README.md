# belBot — Telegram конвертер RUB ↔ BYN

Бот конвертирует суммы между российскими и белорусскими рублями.
Направление выбирается один раз и сохраняется как дефолт для пользователя.
Сменить можно командой или кнопкой.

## Возможности

- Выбор направления: **RUB → BYN** или **BYN → RUB**
- Дефолт хранится в SQLite (не слетает после рестарта)
- Конвертация простым числом: `1000`, `50.5`
- Разовая конвертация с валютой: `1000 RUB`, `50 BYN` (дефолт **не** меняется)
- Курс: НБРБ, fallback ЦБ РФ, кэш 1 час

## Команды

| Команда | Действие |
|---------|----------|
| `/start` | Приветствие + выбор/показ направления |
| `/help` | Справка |
| `/rate` | Текущий курс |
| `/direction` / `/change` | Сменить направление |
| `/my` | Показать текущее направление |

## Быстрый старт (локально)

### 1. Токен у BotFather

1. Открой [@BotFather](https://t.me/BotFather) в Telegram
2. `/newbot` → имя и username
3. Скопируй токен

### 2. Окружение

```bash
cd belBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

В `.env` вставь токен:

```env
BOT_TOKEN=123456:ABC-DEF_your_token_from_BotFather
CACHE_TTL_SECONDS=3600
SQLITE_PATH=data/bot.db
LOG_LEVEL=INFO
```

### 3. Запуск

```bash
python -m bot
```

Бот работает в режиме **long polling**.

## Пример диалога

1. Пользователь: `/start`  
   Бот: приветствие + кнопки «Из RUB (в BYN)» / «Из BYN (в RUB)»

2. Пользователь жмёт «Из RUB (в BYN)»  
   Бот: `Ок. Сейчас: RUB → BYN. Пришли сумму.`

3. Пользователь: `1000`  
   Бот:
   ```
   1000.00 RUB = … BYN
   Курс: 1 RUB = … BYN
   Источник: НБРБ | обновлён: …
   [Сменить направление]
   ```

4. Пользователь: `/direction` → «Из BYN (в RUB)»  
   Бот: `Ок. Сейчас: BYN → RUB. Пришли сумму.`

5. Пользователь: `50`  
   Бот: конвертация 50 BYN → RUB

6. Пользователь: `1000 RUB`  
   Бот: разовая конвертация RUB→BYN, дефолт BYN→RUB **не меняется**

## Docker

```bash
cp .env.example .env
# пропиши BOT_TOKEN в .env
docker compose up -d --build
docker compose logs -f bot
```

Остановка:

```bash
docker compose down
```

Данные направлений: volume `bot-data` → `/app/data/bot.db`.

## Деплой на Railway

1. Залей репозиторий на GitHub
2. [Railway](https://railway.app) → New Project → Deploy from GitHub repo
3. Variables:
   - `BOT_TOKEN` = токен BotFather
   - `SQLITE_PATH` = `/app/data/bot.db`
   - `CACHE_TTL_SECONDS` = `3600`
4. Railway подхватит `Dockerfile`
5. Добавь Volume на путь `/app/data` (чтобы дефолты пользователей жили между редеплоями)
6. Deploy → в логах должно быть `Bot starting (long polling)`

Альтернатива VPS:

```bash
git clone <repo> && cd belBot
cp .env.example .env   # вписать BOT_TOKEN
docker compose up -d --build
```

systemd (без Docker), пример unit:

```ini
[Unit]
Description=belBot Telegram
After=network.target

[Service]
WorkingDirectory=/opt/belBot
ExecStart=/opt/belBot/.venv/bin/python -m bot
Restart=always
EnvironmentFile=/opt/belBot/.env

[Install]
WantedBy=multi-user.target
```

## Структура

```
bot/
  config.py
  main.py
  keyboards.py
  handlers/       # команды, колбэки, конвертация
  services/       # курс + парсинг сумм
  storage/        # SQLite направлений
Dockerfile
docker-compose.yml
.env.example
requirements.txt
```

## Замечания

- Реальный `BOT_TOKEN` не коммить
- Тексты бота на русском
- Без выбранного направления числовые суммы не принимаются (кроме явного `1000 RUB` / `50 BYN`)
