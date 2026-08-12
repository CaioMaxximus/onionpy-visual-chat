FROM alpine:edge

RUN apk update && \
    apk add --no-cache tor


COPY --chown=tor:tor torrc /etc/tor/torrc
COPY --chown=tor:tor tor-docker-boot.sh /tor-docker-boot.sh

RUN chmod +x /tor-docker-boot.sh && \
    chown -R tor:tor /etc/tor /var/lib/tor

USER tor
CMD ["/bin/sh", "/tor-docker-boot.sh"]
