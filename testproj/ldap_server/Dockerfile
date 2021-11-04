FROM osixia/openldap:1.5.0
LABEL maintainer="Dan Yishai <danyi1212@gmail.com>"

ADD bootstrap /container/service/slapd/assets/config/bootstrap
ADD environment /container/environment/01-custom

HEALTHCHECK --interval=30s --timeout=10s \
    CMD ldapsearch -D 'cn=admin,dc=example,dc=org' -w Adm1n! -h localhost -p 389