FROM python:alpine3.17
WORKDIR ./app
RUN pip install flask
RUN pip install flask_restful
RUN pip install pymongo
RUN pip install requests
ENV FLASK_APP=toys-robust.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=80

# Because the Docker Compose bind mounts the host app directory, the host file toys-robust is accessible to
# the service.  we do no need to copy it into the container
# COPY toys-robust.py .
EXPOSE 80

CMD ["flask", "run", "--host=0.0.0.0"]
