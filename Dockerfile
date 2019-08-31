FROM python
ADD requirements.txt requirements.txt
RUN apt install -y libpq-dev && pip install --upgrade pip && pip install -r requirements.txt
ADD meme_contest app/
WORKDIR app
ENTRYPOINT python main.py