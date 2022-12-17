Art exhibit where sensors monitor an area, and plays different sounds depending on where the viewer is standing.

<div style="width: 640px; height: 480px; margin: 10px; position: relative;"><iframe allowfullscreen frameborder="0" style="width:640px; height:480px" src="https://lucid.app/documents/embedded/fce0d5f7-c253-42c3-8bb9-a94bb1083a8c" id="xbqfeEyuO-47"></iframe></div>

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
    - ffmpeg

### Run

```bash
// Start webserver
make master
```
