

![alt text](https://github.com/gasparka/realtime_spectrogram/doc/wify.gif "Wify")
![alt text](https://github.com/gasparka/realtime_spectrogram/doc/diagram.bmp "Wify")

You will need a heat-sink on your LimeSDR-mini to run this!

1. Program the FPGA:

    ```bash
    docker run -it --privileged gasparka/realtime_spectrogram python3 main.py --fpga_init
    ```
    Note: You need to unplug and replug your LimeSDR-Mini!
    
2. Run the application:
    ```bash
    docker run -it --privileged --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" gasparka/realtime_spectrogram python3 main.py --run
    ```
    
3. Once you are done, restore the FPGA:
    ```bash
    docker run -it --privileged gasparka/realtime_spectrogram python3 main.py --fpga_restore
    ```

