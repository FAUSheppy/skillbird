FROM alpine

RUN apk add --no-cache py3-pip
RUN python3 -m pip install --no-cache-dir --break-system-packages waitress
COPY req.txt .
RUN python3 -m pip install --no-cache-dir --break-system-packages -r req.txt

RUN mkdir /app
WORKDIR /app
COPY ./python .

ENTRYPOINT ["python"] 
CMD ["init.py", "--parser-backend", "eventStream"]
