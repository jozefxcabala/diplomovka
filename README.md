# Diploma Thesis Prototype

This repository contains the prototype implementation for the diploma thesis. The system processes video recordings using YOLO for object detection and also utilizes XCLIP for action recognition.

## Installation

To set up the Conda environment and initialize the PostgreSQL database, run the following installation script from the project root `diploma-thesis-prototype/enviroments`:

```bash
bash setup.sh
```

Install node modules:

```bash
cd frontend
npm install

cd ../experiments-ui-frontend
npm install
```

## Running the Prototype
Activate the environment:

```bash
conda activate diploma-thesis-prototype
```

Navigate to the `src` directory:

```bash
cd src
```

Run the prototype with:

```bash
# Run this first to stop any previous sessions in case the last one ended unexpectedly
./run_prototype_ui.sh --stop 
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
- `experiment_backend.log` — FastAPI backend for experiments
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

## Project Structure

The project is organized into the following main directories:

```
diploma-thesis-prototype/
├── data/                          # Input data and models
│   ├── input/                     # Categories, YAML configurations, test video
│   ├── models/                    # Training models (e.g. YOLO)
│   └── output/                    # Output results – detections, segments, visualization
│
├── enviroments/                  # Conda environment setup files for Linux and Windows
│
├── experiments/                  # Evaluation pipeline and scripts
│   ├── payloads/                 # Experiment configurations (JSON)
│   ├── results/                  # Experiment results (metrics, outputs)
│   ├── scripts/                  # Supporting shell scripts (eval, count, run, find...)
│   └── UBnormal/                 # UBnormal dataset (scenes, annotations, videos)
│
├── logs/                         # Log output from all system components
│
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/              # FastAPI routers for different services
│   │   │   ├── core/             # Logic for video processing, detection, recognition
│   │   │   ├── models/           # Pydantic models (request/response, DB)
│   │   │   ├── services/         # Service layer for detection, config, result handling
│   │   │   └── utils/            # Helper utilities (file handling, conversions)
│   │   └── requirements.txt      # Python dependencies for the backend
│
│   ├── frontend/                 # Main React frontend UI
│   │   ├── components/           # Modals, detection display, inputs
│   │   └── pages/                # StartupScreen, FirstScreen, SecondScreen, etc.
│
│   ├── experiments-ui-frontend/  # Experimental React frontend
│       ├── components/           # Parameter modal, charts, result cards
│       └── ExperimentsPage.tsx   # Main experiments interface
│
├── run_prototype_ui.sh           # Main script for launching backend and frontend
├── setup.sh                      # Setup script for installing dependencies
```