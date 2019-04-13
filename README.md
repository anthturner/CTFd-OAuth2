# CTFd OAuth2 Authentication Plugin

Add OAuth2 authentication to CTFd 2.x using compatible providers. Users can be linked between the CTFd User database and the OAuth provider; these users can be created on the fly or not.

✅ `Flask-Dance` is required.

## Supported Providers:
* `azure` (Azure Active Directory)
* `github` (GitHub)
* ... and any other Flask-Dance provider, with a little work!

## Configuration
The following configuration options must be defined in `config.py`:
```
OAUTHLOGIN_CLIENT_ID - OAuth2 Provider Client ID
OAUTHLOGIN_CLIENT_SECRET - OAuth2 Provider Client Secret
OAUTHLOGIN_PROVIDER - OAuth2 Provider name (see 'Supported Providers' above)
OAUTHLOGIN_CREATE_MISSING_USER - If the plugin should create a CTFd user to link to the OAuth2 user
```

## Extensibility:
Adding a new provider is as simple as adding entries to the two lambda dictionaries, `provider_blueprints` and `provider_users`.

```python
# Key is the OAuth provider name
# Value is a lambda that returns a Blueprint for the authentication controller
provider_blueprints = {
    'azure': lambda: flask_dance.contrib.azure.make_azure_blueprint(
        login_url='/azure',
        client_id=oauth_client_id,
        client_secret=oauth_client_secret,
        redirect_url=authentication_url_prefix + "/azure/confirm")
}

# Key is the OAuth provider name
# Value is a lambda that returns a User object mapped from the OAuth user, or None if the user doesn't exist and creation is disabled.
provider_users = {
    'azure': lambda: 
        get_bridge_user(
            displayName=flask_dance.contrib.azure.azure.get("/v1.0/me").json()["displayName"],
            email=flask_dance.contrib.azure.azure.get("/v1.0/me").json()["userPrincipalName"])
}
```