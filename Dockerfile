FROM python:3.8

ENV PYTHONUNBUFFERED=1

# Install pipenv
RUN pip install pipenv

# Set working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Install dependencies with pipenv
RUN pipenv install

RUN pip install signalrcore

# Copy the rest of the app's source code
COPY . /app

# Set the command to run the app
CMD ["pipenv", "run", "start", "TOKEN=${LAB02_TOKEN}"]
