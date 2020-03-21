# Telegram Bot Setup

## Chat with bot father

[Offical Instructions](https://core.telegram.org/bots#6-botfather)

Once you acquired the bot token, remember to turn off the privacy mode. See [here](https://core.telegram.org/bots#privacy-mode)
for details. Go chat with botfather, and there will be one button to toggle privacy mode for your bot. 

## Install extension

```bash
pip install umr-telegram-driver
```

## Config under Driver section

```yaml
Extensions:
  - umr_telegram_driver
Driver:
  Telegram:  # this name can be change, and the forward list should be using this name
    Base: Telegram  # this is the base driver name, do not change
    BotToken: asdasdsadsadsadsad  # your bot token
```