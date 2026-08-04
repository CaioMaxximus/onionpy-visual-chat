FROM alpine:edge

RUN apk update && \
    apk add --no-cache tor


EXPOSE 9050 9051

USER tor
ENTRYPOINT ["tor"]

CMD ["--defaults-torrc", "etc/torrc" , \
    "SocksPort" , "0.0.0.0:9050" , \
    "ControlPort" , "0.0.0.0:9051" ,\
    "CookieAuthentication" , "0"]