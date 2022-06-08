FROM python:3.8
WORKDIR /tmp/project/smart-grocery-api
COPY . /tmp/project/smart-grocery-api
RUN pip install pipenv
RUN pipenv install
#RUN pipenv shell
ENTRYPOINT pipenv run python -m flask run
