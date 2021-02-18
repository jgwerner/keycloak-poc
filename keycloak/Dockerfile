FROM quay.io/keycloak/keycloak:latest

USER jboss

## adds auth and keycloakc/auth paths to config
RUN sed -i -e 's/<web-context>auth<\/web-context>/<web-context>keycloak\/auth<\/web-context>/' \
  "${JBOSS_HOME}/standalone/configuration/standalone.xml"
