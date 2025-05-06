# Diploma Thesis Prototype

This repository contains the prototype implementation for the diploma thesis. The system processes video recordings using YOLO for object detection and also utilizes XCLIP for action recognition.

## Installation

To set up the Conda environment, run the following command inside `diploma-thesis-prototype/enviroments`:

```bash
conda env create -f diploma-thesis-prototype-env.yml
```

Once the installation is complete, activate the environment:

```bash
conda activate diploma-thesis-prototype
```

Install node modules:

```bash
cd frontend
npm install

cd ../experiments-ui-frontend
npm install
```

## Running the Prototype

Navigate to the `src` directory:

```bash
cd src
```

Run the prototype with:

```bash
# Starts the full prototype: HTTP video server, FastAPI backend, and standard React frontend
./run_prototype_ui.sh
```

These commands launch various parts of the prototype UI stack:

```bash
# Starts only the FastAPI backend (also includes the HTTP video server)
./run_prototype_ui.sh --backend
```

```bash
# Starts only the standard React frontend
./run_prototype_ui.sh --frontend
```

```bash
# Starts the prototype in production mode (no reload flags)
./run_prototype_ui.sh --prod
```

```bash
# Starts the backend and the UI used for experiments (on port 3001)
./run_prototype_ui.sh --experiments
```

```bash
# Stops all running components (HTTP server, backend, frontends)
./run_prototype_ui.sh --stop
```

### Logs

When running the script, logs will be written to:

- `backend.log` — FastAPI backend
- `frontend.log` — Standard React frontend
- `experiments-ui-frontend.log` — Experimental frontend (if used)
- `http_server.log` — Simple HTTP server for video hosting

Use `tail -f <logfile>` to monitor logs in real time.


## Notes

- Folder `data/input` contains a sample video, along with predefined categories and model settings used for demonstration purposes.
- Ensure all dependencies are correctly installed within the Conda environment.
- If you encounter any issues, verify that you are in the correct environment by running:
  
  ```bash
  conda info --envs
  ```
  
  The active environment should be `diploma-thesis-prototype-env`.