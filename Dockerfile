FROM alpine:edge

RUN apk update && \
    apk add --no-cache tor

COPY torrc /etc/tor/torrc

USER tor

CMD ["tor", "-f", "/etc/tor/torrc"]

