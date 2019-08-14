FROM python:3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY input.txt ./
COPY Stationen.txt ./
COPY templates/index.html ./templates/

COPY . .

CMD [ "python", "klima_flask.py" ]