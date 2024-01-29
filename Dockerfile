FROM 194943407731.dkr.ecr.eu-west-1.amazonaws.com/python:latest

WORKDIR /app

COPY requirements.txt /app/
COPY requirements-tg.txt /app/
RUN pip install -r /app/requirements.txt
# install aiogram separately due to aiohttp version conflict
RUN pip install -r /app/requirements-tg.txt

COPY joeBot /app/joeBot
COPY content /app/content
COPY AvaxBot.py /app/
COPY JoeDiscordBot.py /app/
COPY JoeTelegramBot.py /app/
COPY run.py /app/

CMD ["python", "./run.py"]