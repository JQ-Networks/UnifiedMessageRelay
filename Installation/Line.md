# Line Bot Setup

## Sign up line developer console

Follow [this guide](https://cloud.google.com/dialogflow/docs/integrations/line) until you get the following stuff:

- Channel id (Under "Basic Settings")
- Bot token (Channel access token (long-lived), need to click claim once under "Messaging API")
- WebHookToken (Channel secret, under "Basic Settings")

# Set up certificates for HTTPS

You have to make sure that your running environment has public access, and it is also bound to a domain.

If you have your own certificate, skip this part. If not, try to use [LetEncrypt](https://github.com/acmesh-official/acme.sh).

If you are having issue in this part, follow guides on the link above.

After this part is done, more stuffs are ready:

- HTTPS CA Cert (ca.cer)
- HTTPS Private Key (example.com.key)
- HTTPS Public Key  (example.com.cer)

## Config under Driver section

```yaml
Driver:
  Line:  # this name can be change, and the forward list should be using this name
    Base: Line  # do not change this
    ChannelID: sdarq3rcar323r2r23r
    BotToken: 123dff23rr23r23r23rr
    WebHookToken: 43r23r23rf23r23r23r2
    WebHookURL: https://example.com  # must not include /callback
    WebHookPort: 41443
    HTTPSCert: /root/.acme.sh/example.com/example.com.cer  # all three are full path
    HTTPSKey: /root/.acme.sh/example.com/example.com.key
    HTTPSCA: /root/.acme.sh/example.com/ca.cer
```