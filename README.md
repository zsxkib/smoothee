# smoothee
Video frame-interpolation Python package utilizing Replicate models.

## System Requirements

- **GPU Support**: This library requires an Nvidia GPU for optimal performance.
- **Python Version**: Python 3.10 is recommended for compatibility.
- **System Packages**: 
  - `libgl1-mesa-glx` (Install via your system's package manager)
  - `ffmpeg` (Instructions provided below)

## Installation

First, ensure that you have Python 3.10 installed. Then, follow these steps:

1. **Install System Packages**:
   - Update your system package list: 
     ```bash
     apt-get update
     ```
   - Install `ffmpeg`:
     ```bash
     apt-get install -y ffmpeg
     ```
   - Install `pget` (a fast alternative to curl/wget for downloading weights from Replicate fast):
     ```bash
     curl -o /usr/local/bin/pget -L "https://github.com/replicate/pget/releases/download/v0.3.0/pget" && chmod +x /usr/local/bin/pget
     ```
      - This update makes it clear that pget is a fast alternative to curl and wget for downloading weights from Replicate, and it provides the command to install pget. It also explains what will happen if the user skips this step.

2. **Install Python Dependencies**:
   - Upgrade pip to its latest version:
     ```bash
     pip install --upgrade pip
     ```
   - Install the required Python packages:
     ```bash
     pip install imageio[ffmpeg]
     pip install tensorflow==2.8.0
     ```
   - Note: Due to a known issue, TensorFlow 2.8.0 needs to be installed separately.

3. **Install Smoothee**:
   - Clone the repository and navigate to the project directory.
   - Install the package using pip:
     ```bash
     pip install .
     ```

## Python Dependencies

While these are automatically installed during the setup, here's a list of key Python packages used:

- TensorFlow 2.8.0
- TensorFlow Datasets 4.4.0
- TensorFlow Addons 0.16.1
- absl-py 0.12.0
- gin-config 0.5.0
- parameterized 0.8.1
- mediapy 1.0.3
- scikit-image 0.19.1
- pget 0.3.0

## Usage

To use Smoothee in your project:

```python
from pathlib import Path
from smoothee import Film

# Initialize the Film and specify the input and output files
film_interp = Film()
input_mp4_path = Path("./input.mp4")  # x fps video with y frames
output_file_path = Path("./smoothee_output.mp4")

# Perform frame interpolation and print the path to the output video
output_file = film_interp.interp(
    input_mp4_path=input_mp4_path,
    output_mp4_path=output_file_path,
    playback_frames_per_second=24,
    num_interpolation_steps=1,
)

print(
    f"Interpolated video saved at: {output_file_path}"
)  # 2*x fps video with (2*y-1) frames
```
