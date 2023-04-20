# TrainingBot
Это телеграмм бот для помощи отслеживания съеденных калорий. В котором реализованн сбор основной информации о пользователе, анализ его текущего рациона, составление программы похудения и разного рода напоминания.  
На данный момент осталось реализовать построение программы для вариантов удержания и набора веса.  
`https://t.me/f1ttnesBot`

## Installation

Clone the repository and go to it on the command line:

```
git clone https://github.com/yandex-praktikum/kittygram_backend.git
```

```
cd kittygram_backend
```

Create and activate a virtual environment:

```
python3 -m venv env
```

```
source env/scripts/activate
```

```
python3 -m pip install --upgrade pip
```

Install dependencies from a file requirements.txt:

```
pip install -r requirements.txt
```

Perform migrations:


```
python3 manage.py migrate
```

`Also create an .env file in the /TrainingBot directory and specify the data for postgresql and the bot token.`  
Launch a project:

```
python3 manage.py bot
```
