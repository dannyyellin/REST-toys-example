FROM python:alpine3.17
WORKDIR ./app
COPY toys.py .
RUN pip install Flask
ENV FLASK_APP=toys.py
ENV FLASK_RUN_PORT=8001
#ENV NINJA_API_KEY - if required
EXPOSE 8001
CMD ["flask", "run", "--host=0.0.0.0"]
