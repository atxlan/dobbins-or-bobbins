FROM python:3.9.6-slim
ENV PATH="/usr/src/venv/bin:$PATH"
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt
COPY . /usr/src/app
