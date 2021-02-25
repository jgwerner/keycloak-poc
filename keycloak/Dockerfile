FROM jboss/keycloak:latest

USER jboss

ENV JBOSS_HOME='/opt/jboss/keycloak'

# Adds access-log to ${JBOSS_HOME}/standalone/
COPY standalone.xml "${JBOSS_HOME}/standalone/configuration/standalone-ha.xml"
COPY standalone-ha.xml "${JBOSS_HOME}/standalone/configuration/standalone-ha.xml"

## adds auth and keycloakc/auth paths to config
RUN sed -i -e 's/<web-context>auth<\/web-context>/<web-context>keycloak\/auth<\/web-context>/' \
  "${JBOSS_HOME}/standalone/configuration/standalone.xml"
RUN sed -i -e 's/<web-context>auth<\/web-context>/<web-context>keycloak\/auth<\/web-context>/' \
  "${JBOSS_HOME}/standalone/configuration/standalone-ha.xml"
