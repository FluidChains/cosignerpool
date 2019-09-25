#!/bin/sh

while [ ! -f /etc/letsencrypt/live/cosigner/fullchain.pem ]
do
	echo "sleeping"
	sleep 5
done

echo $NGINX_HOST
/bin/bash -c "envsubst < /etc/nginx/conf.d/CosignerSSL.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
