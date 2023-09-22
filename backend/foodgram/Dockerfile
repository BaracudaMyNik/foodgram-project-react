FROM python:3.7-slim
WORKDIR /app
COPY backend/foodgram/requirements.txt ./
RUN pip3 install -r requirements.txt --no-cache-dir
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


# old
#FROM python:3.7-slim
#WORKDIR /app
#COPY backend/foodgram/requirements.txt ./
#RUN pip3 install -r requirements.txt --no-cache-dir
#COPY backend/foodgram/ ./
#CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
