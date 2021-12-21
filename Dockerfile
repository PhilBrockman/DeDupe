# Slim version of Python
FROM python:latest

# Download Package Information
RUN apt-get update -y

# Install Tkinter
RUN apt-get install tk -y

COPY ./basic.py      ./basic.py
# RUN python basic.py