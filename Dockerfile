FROM python
ADD requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD meme_contest app/
WORKDIR app
ENTRYPOINT python models.py
ENTRYPOINT python main.py