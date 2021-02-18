FROM quay.io/keycloak/keycloak:latest

USER jboss

ENV JBOSS_HOME='/opt/jboss/keycloak'

## adds auth and keycloakc/auth paths to config
RUN sed -i -e 's/<web-context>auth<\/web-context>/<web-context>keycloak\/auth<\/web-context>/' \
  "${JBOSS_HOME}/standalone/configuration/standalone.xml"
RUN sed -i -e 's/<web-context>auth<\/web-context>/<web-context>keycloak\/auth<\/web-context>/' \
  "${JBOSS_HOME}/standalone/configuration/standalone-ha.xml"
