FROM node:10.16.3-alpine AS build
LABEL maintainer Pat Dayton "pat.dayton@utdallas.edu"

RUN mkdir /home/app
WORKDIR /home/app

COPY . .

RUN apk update

# Install the necessary dependencies
# The --no-cache option allows you to not cache the index locally.
# ...this keeps the image small.
RUN apk add --no-cache bash
RUN apk add --no-cache postgresql
RUN apk add --no-cache postgresql-contrib
RUN apk add --no-cache --virtual .gyp \
    python \
    make \
    python

# Installing all dependencies
RUN npm install


RUN apk del .gyp

CMD ["npm", "start"]
