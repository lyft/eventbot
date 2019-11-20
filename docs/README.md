# Developer-local docs build

```bash
./docs/build.sh
```

The output can be found in `generated/docs`.

# How the Eventbot website and docs are updated

1. The docs are published to [docs/eventbot/latest](https://github.com/lyft/eventbot.github.io/tree/master/docs/eventbot/latest)
   on every commit to master. This process is handled by Travis with the
  [`publish.sh`](https://github.com/lyft/eventbot/blob/master/docs/publish.sh) script.

2. The docs are published to [docs/eventbot](https://github.com/lyft/eventbot.github.io/tree/master/docs/eventbot)
   in a directory named after every tagged commit in this repo. Thus, on every tagged release there
   are snapped docs.
