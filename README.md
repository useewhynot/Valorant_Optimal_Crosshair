# Valorant_Optimal_Crosshair
**THIS REPOSITORY IS NOT ACTIVELY MAINTAINED**
## Requirements:
- Python (I used Python 3.8, you probably can get away with newer versions)
- pip

## Installation
Run the following command, hopefully within a virtual or conda environment to save yourself the headache
```bash
pip install -r requirements.txt
```

## Running the Script
### Command Syntax
```
python main.py [path to your data video or folder of videos] --sample-rate [insert sample rate]
```
This script takes a long time to run and progress bars don't really work since there's no way to tell how long the video is before you iterate through it (RIP tqdm)
Long story short, be patient when this thing runs
