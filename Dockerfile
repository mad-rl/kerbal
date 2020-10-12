FROM python:3.8

WORKDIR /kerbal

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install gym

COPY src/ .
COPY saved_games/ ./saved_games/

ENV PYTHONPATH=./

CMD [ "python", "./start.py" ]