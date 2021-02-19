# IllumiDesk with SAML v2.0

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Build and Start

1. Build:

```bash
docker-compose build --no-cache
```

2. Start:

```bash
docker-compose up -d
```

## Dev Setup

### 1. Create and Configure Keycloak Realm

> **NOTE**: a working local test should use TSL termination. You can emulate TSL termination by using a third party service such as [`ngrok`](https://ngrok.com/download) to publish local ports to a publicly accesible domain with `https://...`.


1. Log into admin portal at `https://<my-random-id.ngrok.io>/keycloak/auth`.
2. Create new realm by navigating to `Home --> Realm Drop Down (top left) --> Create New Realm`.
3. Enter Realm Name, such as `illumidesk`.
4. Click on `Configure` --> `Realm Settings`.
5. Ensure realm is toggled to `Enable`.
6. (Optional) Add `Display Name` and `HTML Display Name` values.
7. Click on `Login` tab.
8. Select the `none` setting for `Require SSL`.
9. Click on `Save`

### 2. Create Keycloak Realm Client

**General Settings**

1. Click on `Home` --> `Configure` --> `Clients` --> `Create`. The `Create` button is on the top right hand portion of the page.
2. Enter `Client ID`, such as `illumidesk-hub`
3. Ensure the `Enabled` option is toggled to `ON`.
4. (Optional) Add `Name` and `Description`.
5. Ensure the `Client Protocol` option is set to `openid-connect` (default).
6. Ensure the `Access Type` option is set to `credentials` (`public` is default).
7. Ensure `Standard Flow Enabled` is toggled to `ON`.
8. Ensure `Direct Access Grants Enabled` is toggled to `ON`.
9. For `Root URL` enter `https://<my-random-id.ngrok.io>`.
10. For `Base URL` enter `/`.
11. For `Web Origins` enter `*` (any origin).

### 3. Create External SAML v2.0 Identity Provider

Instructions to set up a SAML v2.0 Identity Provider (IdP) vary depending on the vendor. Below is a list of the vendors we have tested this setup with.

**[Auth0](https://auth0.com)**

1. Create a new `Application` by clicking on `Applications` --> `+ Create Application`
2. Enter an application name, such as `IllumiDesk SAML`
3. Select the `Regular Web Application` option
4. Click on the `Create` button
5. In the `Application URIs` section, ensure the `Token Endpoint Authentication Method` option has `Post` selected.
6. In the `Application URSs` section, enter the `Allowed Callback URLs` value. This value should have the following format (the example below assumes the host is `https://<my-random-id.ngrok.io>` and the realm is `illumidesk`)

```
http://127.0.0.1:8080/keycloak/auth/realms/illumidesk-realm/broker/saml/endpoint
```

7. At the bottom of the page, click on the `Advanced Settings` option.
8. Click on the `Endpoints` tab.
9. Take note of the `SAML Protocol URL`. It should look similar to: `https://illumidesk.auth0.com/samlp/metadata/C2Nb4pMdbeAmwLy3dPhr9uB5KMep34ct`
10. Click on the `Save` button at the bottom of the page.
11. Click on the `Addons` tab.
    1.  Turn on the `SAML2 Web App` by toggling the button to on (green).
    2.  Click on the `SAML2 Web App` card to open the `Settings` and `Usage` modal.
    3.  Click on the `Settings` tab and enter the `Application Callback URL` for your application. For example, if your host is `https://<my-random-id.ngrok.io>` and your Realm is `illumidesk`, then your `Application Callback URL` should be `https://<my-random-id.ngrok.io>/keycloak/auth/realms/illumidesk/broker/saml/endpoint`.
12. Click on the `Connections` tab.
    1.  Enable the `Username-Password-Authentication` by toggling the button so that it's green.
    2.  (Optional) Enable other connections, such as other Social Authentication services.

> **Note**: the `Application Callback URL` from section `11.2` is also known as the `Assertion Consumer Service URL`, the `Post-back URL`, or `Callback URL`.

### 4. Create Keycloak Realm Identity Provider with SAML v2.0

1. Click on `Home` --> `Configure` --> `Identity Providers`
2. Create a new SAML v2.0 provider by selecting the `User-defined` --> `SAML v2.0`
3. Enter `saml` for the `Alias`
4. (Optional) Enter a `Display Name`, such as `IllumiDesk SAML v2.0 Identity Provider (IdP)`
5. Ensure the `Enabled` option is toggled to `ON`.
6. Ensure the `Trust Email` option is toggled to `ON`.
7. The `Service Provider Entity ID` is populated by default. The value should append the `/keycloak/auth/realms/illumidesk` to the root URL. For example, `https://<my-random-id.ngrok.io>/keycloak/auth/realms/illumidesk`.
8. In the `SAML Config` section, add the `Service Provider Entity ID` to reflect the Keycloak realm you set up in **section 1** above.
9. In the `SAML Config` section, add the `Single Sign-On Service URL`. This value should match the value for the SAML IdP protocol URL. For example, with `Auth0` this setting is called `SAML Protocol URL` in `Applications` --> `<SAML Application Name>` --> `Settings` --> `Advanced Settings` --> `Endpoints` --> `SAML`. The value should be similar to `https://auth.illumidesk.com/samlp/C2Nb4pMdbeAmwLy3dPhr9uB5KMep34ct`.
10. Select `Unspecified` for `NameID Policy Format`.
11. For `Principal Type` select `Subject NameID`.
12. Ensure `HTTP-POST Binding Response`, `HTTP-POST Binding for AuthnRequest`, and `HTTP-POST Binding Logout` are all toggled to `ON`.
13. Add a reasonable clock skew tolerance window in the `Allowed clock skew` field, such as `60`.
14. Click on `Save` at the bottom of the page.

### 5. Configure JupyterHub

1. Copy the `env.example` file and create a `.env` file.
2. Update the `.env` file with your values:
   1. `JUPYTERHUB_HOST`: the external facing JupyterHub host URL, such as `https://<my-random-id.ngrok.io>`.
   2. `KEYCLOAK_INTERNAL_HOST`: the internal Keycloak service scheme, name and port. For example: `https://keycloak:8080`.
   3. `KEYCLOAK_EXTERNAL_HOST`: the external Keycloak scheme, host, and port. This is the endpoint that For example:  `https://127.0.0.1:8080`.
   4. `KEYCLOAK_REALM`: the Keycloak Realm name, such as `illumidesk`.
   5. `OAUTH_CLIENT_ID`: the name of the Keycloak client configured with the Keycloak Realm in **Section 4** above, such as `illumidesk-hub`.
   6. `JUPYTERHUB_CRYPT_KEY`: the JupyterHub crytographic key used to encrypt the `auth_state` when the authentication dictionary is persisted from the Authenticator to the Spawner using the `JupyterHub.auth_state_enabled = True` setting. Create a secure random string with the `openssl rand -hex 32` command from your preferred terminal. If you don't have access to the `openssl` command, any random value should suffice. **However, please change before configuring the environment for Production!**
