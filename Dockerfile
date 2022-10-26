FROM sanicframework/sanic:3.9-latest
RUN apk --update add gcc libc-dev
WORKDIR /sanic
COPY ./app /sanic/app
COPY ./main.py /sanic/main.py
COPY ./requirements.txt /sanic/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python", "main.py"]