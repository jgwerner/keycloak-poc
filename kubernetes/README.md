## Keycloak + ingress-nginx

- Create a new namespace, called `ingress-nginx`:

```bash
kubectl create namespace ingress-nginx
```

- Create a second namespace called `keycloak` for the keycloak service, deployment, and ingress resource:

```bash
kubectl create namespace keycloak
```

- Create TLS private key, root, and certificate for the nginx resource to enable TLS termination with Nginx (replace `your.domain.tld` with the domain you would like to use to access the service):

```bash
export KEY_FILE=keycloak.key
export CERT_FILE=keycloak.crt
export HOST=your.domain.tld
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${KEY_FILE} -out ${CERT_FILE} -subj "/CN=${HOST}/O=${HOST}"
```

- Create the secret in the namespace where the application is deployed:

```bash
kubectl create secret tls ${CERT_NAME} --key ${KEY_FILE} --cert ${CERT_FILE} -n {namespace-where-app-is-deployed}
```

- Deploy the ingress resource and the app itself:

```bash
kubectl apply -f ingress-nginx-controller.yaml
kubectl apply -f keycloak-ingress.yaml
kubectl apply -f keycloak.yaml
```

Then, navigate to the application to test the Keycloak redirect:

https://your.domain.tld/auth/admin

The a login screen is displayed, you are good to go.
