FROM python:3.8.10

WORKDIR /code


# Install ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN export PATH="$PATH:/opt/mssql-tools/bin"
RUN apt-get install -y unixodbc-dev
RUN apt-get install -y libgssapi-krb5-2

# Get Firefox and Gecko Driver
RUN apt-get install -y firefox-esr
# RUN apt-get install -y firefox-geckodriver

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
RUN tar -xvzf geckodriver*
RUN chmod +x geckodriver
RUN cp geckodriver /usr/local/bin/
RUN apt-get install -y xvfb
RUN Xvfb :99 &
RUN export DISPLAY=:99

# Python Libraries
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 1102 5000

CMD ["bash", "start.sh"]
