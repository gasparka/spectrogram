# BUILD

```bash
docker build -t realtime_spectrogram --no-cache  .
```

# RUN

```bash
docker run -it --privileged --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" realtime_spectrogram:latest
```

