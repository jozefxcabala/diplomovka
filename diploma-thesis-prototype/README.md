# Diploma Thesis Prototype

This repository contains the prototype implementation for the diploma thesis. The system processes video recordings using YOLO for object detection.

## Installation

To set up the Conda environment, run the following command:

```bash
conda env create -f diploma-thesis-prototype-env.yml
```

Once the installation is complete, activate the environment:

```bash
conda activate diploma-thesis-prototype-env
```

## Running the Prototype

Navigate to the `src` directory:

```bash
cd src
```

Run the prototype with:

```bash
./run_prototype.sh --video_path path_to_input_video
```

## Notes

- Place the input video in the `data/input` folder before running the prototype.
- Ensure all dependencies are correctly installed within the Conda environment.
- If you encounter any issues, verify that you are in the correct environment by running:
  
  ```bash
  conda info --envs
  ```
  
  The active environment should be `diploma-thesis-prototype-env`.