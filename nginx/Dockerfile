FROM ubuntu:18.04
# install nginx
RUN apt-get -y upgrade && apt-get -y update && apt-get -y install python3 && apt-get -y install python3-pip
RUN apt-get install -y nginx
# deamon mode off
# volume
#VOLUME ["/etc/nginx/sites-enabled", "/etc/nginx/certs", "/var/log/nginx"]
# expose ports
EXPOSE 80 443
# add nginx conf
ADD ./default.conf /etc/nginx/sites-available/default
ADD ./nginx.conf /etc/nginx/nginx.conf
RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf
RUN chown -R www-data:www-data /var/lib/nginx
WORKDIR /etc/nginx
#RUN nginx -t