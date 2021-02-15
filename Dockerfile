FROM node:12.10.0-alpine

COPY . /root/

WORKDIR /root/

CMD ["sleep", "100000"]