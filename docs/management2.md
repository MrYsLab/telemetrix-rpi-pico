# Cleanly Shutting Down

## shutdown
You should always call the shutdown method to exit your application cleanly and
ensure that any streaming data coming from the Pico is halted.

```python
 async def shutdown(self)

    This method attempts an orderly shutdown.
    If any exceptions are thrown, they are ignored.
```
## Example: All the examples call shutdown.

<br>
<br>

Copyright (C) 2021 Alan Yorinks. All Rights Reserved.
