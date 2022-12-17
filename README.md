Art exhibit where sensors monitor an area, and plays different sounds depending on where the viewer is standing.

<p align="center">
    <img width="640px"src="docs/overview.png">
</p>


## Hardware 🔨

### Electrical

- Arduino Uno or equivalent board
- Ultrasonic sensor → PIN 3 and PIN 4
- PIR motion sensor → PIN 2

## Software 🍦

### Dependencies

- Arduino C
- Make
- Python
    - Flask
    - Flask CORS
    - Flask API
	- Requests
- ffmpeg

### Run

```bash
// Start webserver
make master
```
