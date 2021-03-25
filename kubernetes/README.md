## Keycloak + JupyterHub + ingress-nginx + AWS NLB

### Overview

This document provides instructions to set up a basic working version of IllumiDesk's stack with:

- [AWS EKS](https://aws.amazon.com/eks/) with Kubernetes v1.18+
- [AWS NLB](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html)
- Ingress controller with [ingress-nginx](https://kubernetes.github.io/ingress-nginx/) v0.44.0+
- [Keycloak](https://www.keycloak.org/docs/latest/server_admin/) v2.0.0+ for authentication services
- [JupyterHub](https://jupyterhub.readthedocs.io/en/latest/) for workspace orchestration

## Installation and Configuration

### Configure Namespaces

Ensure you have access to the the AWS EKS cluster with the `kubectl` CLI tool. [Refer to AWS's official documentation](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html) for detailed instructions.

- Create a new namespace, called `ingress-nginx`. This namespace is used to manage the globally accessibly ingress controller:

```bash
kubectl create namespace ingress-nginx
```

- You can install the stack in the `default` namespace or select another. If you would like to use a namespace other than `default`, then create the new namespace using the kubectl CLI. For example:

```bash
kubectl create namespace keycloak
```

### Configure TLS Termination

#### Option 1: Configure ingress-ngnix with TLS Termination with NLB

# Keycloak with ingress-nginx

## Ingress Controller

1. **Confirm ingress-nginx annotations**: ensure the annotations are inline with the example output provided by the official ingress-nginx helm chart but replace `elb` with `nlb` as currently defined. For clarity, the [annotations are on these lines](https://github.com/kubernetes/ingress-nginx/blob/b0b14d01b6d8b0beaecc80b0c9cb42f24beaf1e8/hack/generate-deploy-scripts.sh#L92-L100).
2. **Confirm ingress-nginx ConfigMap**: k/v's (located within the data key) are equivalent to the settings provided by [this section of the official helm chart output](https://github.com/kubernetes/ingress-nginx/blob/b0b14d01b6d8b0beaecc80b0c9cb42f24beaf1e8/hack/generate-deploy-scripts.sh#L112-L119).
3. Confirm that the ingress controller's Service has the correct target ports (located in the spec section).

> **NOTE**: This is an important piece of the puzzle when configuring ingress-nginx using NLB with TLS termination using AWS's ACM. Essentially, we are configuring the ingress-controller service **to use http when the source port is https/443**.

```yaml
kind: Service
apiVersion: v1
metadata:
    ... ommitted for brevity
spec:
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: tohttps <-- This is new
    - name: https
      port: 443
      protocol: TCP
      targetPort: http
```

4. Update the Ingress Controller's ConfigMap with the correct key/value pairs [as exemplified here](https://github.com/kubernetes/ingress-nginx/blob/master/hack/generate-deploy-scripts.sh#L112-L119). Ensure the ingress IP CIDR (`proxy-real-ip-cidr`) reflects your setup, for example, `0.0.0.0/0`.

## Ingress Resource

Update the Ingress resource in the namespace where the PoC application is running. Make sure the following settings are in place:

- The `tls` spec is required when terminating TLS with the external load balancer.
- The `hosts`/`host` keys should be associated to the external facing URL (the example below uses `demo.illumidesk.com`)
- Keycloak's service is available with the `/auth` path. The port is the default port for Keycloak's service (`8080`). The service name in this case is `keycloak`.
- JupyterHub's service is available with the `/jupyter` path. The port is the _external_ JupyterHub port (`80`). The service name for this external-facing services is `proxy-public`.

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: ingress-default
  annotations:
    # use the shared ingress-nginx
    kubernetes.io/ingress.class: "nginx"
spec:
  tls:
    - hosts:
      - demo.illumidesk.com
  rules:
  - host: demo.illumidesk.com
    http:
      paths:
      - path: /auth
        backend:
          serviceName: keycloak
          servicePort: 8080
      - path: /jupyter
        backend:
          serviceName: proxy-public
          servicePort: 80
```

## Keycloak Service

This is a very basic setup to launch and run Keycloak as a Kubernetes service. Make sure the following settings are in place:

- The `http` port corresponds to the Ingress resource port for the Keycloak service.
- The Service type is `ClusterIP` or `NodePort`, not `LoadBalancer`.
- 

```yaml
apiVersion: v1
kind: Service
metadata:
  name: keycloak
  labels:
    app: keycloak
spec:
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  selector:
    app: keycloak
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: default
  labels:
    app: keycloak
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:12.0.4
        env:
        - name: KEYCLOAK_USER
          value: "admin"
        - name: KEYCLOAK_PASSWORD
          value: "admin"
        - name: PROXY_ADDRESS_FORWARDING
          value: "true"
        ports:
        - name: http
          containerPort: 8080
        - name: https
          containerPort: 8443
        readinessProbe:
          httpGet:
            path: /auth/realms/master
            port: 8080
```
