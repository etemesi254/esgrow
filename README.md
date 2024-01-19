
### Authorization method.

Once you have a route that requires authorizarion you should specify the authorization in the heasder

THe format is the following

```text
Authorization: Token {TOKEN_KEY}
```


If you are running Django on Apache using mod_wsgi you have to add
```text
WSGIPassAuthorization On
```

in your `httpd.conf` Otherwise, the authorization header will be stripped out by mod_wsgi