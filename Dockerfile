FROM python:3
RUN mkdir /tromino
RUN useradd -ms /bin/bash tromino
USER tromino
ADD . /tromino
WORKDIR /tromino
RUN pip install --user -r requirements.txt
WORKDIR /tromino/src
EXPOSE 8080
CMD python tromino.py