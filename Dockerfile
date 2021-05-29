FROM python:3.9

ENV TERM xterm-256color
ENV PYTHONDONTWRITEBYTECODE="true"

WORKDIR /example_scripts

COPY python/requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT [ "python" ]
CMD [ "menu.py"]