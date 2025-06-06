/****
 * ExperimentsPage component
 *
 * This page provides an interface for running and visualizing anomaly detection experiments
 * on the UBnormal dataset. It allows users to:
 * - Set custom experiment parameters via a modal.
 * - Launch the experiment by sending a request to the backend.
 * - Visualize evaluation results with bar charts (counts and metrics).
 * - Download results as a JSON file.
 *
 * State:
 * - request: input parameters for the backend experiment API.
 * - results: evaluation output (precision, recall, F1, etc.).
 * - loading: whether the experiment is running.
 * - isModalOpen: whether the parameter modal is open.
 */
import React, { useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
} from "chart.js";
import "./ExperimentsPage.css";
import ExperimentParamsModal from "./components/ExperimentParamsModal";

ChartJS.register(BarElement, Tooltip, Legend, CategoryScale, LinearScale);

interface ExperimentResults {
  total_detections: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  precision: number;
  recall: number;
  f1_score: number;
}

interface UBnormalExperimentRequest {
  dataset_path: string;
  model_path: string;
  num_segments: number;
  categories: string[];
  threshold: number;
  skip_frames: boolean;
  num_of_skip_frames: number;
  confidence_threshold: number;
  top_k: number;
  batch_size: number;
  frame_sample_rate: number;
  processing_mode: string;
}

const defaultRequest: UBnormalExperimentRequest = {
  dataset_path: "experiments/UBnormal",
  model_path: "data/models/yolo11n.pt",
  num_segments: 8,
  categories: [
    "a person wearing a helmet and an orange vest is walking",
    "a person wearing a helmet and an orange vest is dancing",
    "a person wearing a helmet and an orange vest is standing in place",
    "a person wearing a helmet and an orange vest is jumping",
    "a person wearing a helmet and an orange vest is running",
    "a person wearing a helmet and an orange vest is fighting",
    "a person wearing a helmet and an orange vest have something in hand",
    "a person wearing a helmet and an orange vest is lying in the ground",
    "a person wearing a helmet and an orange vest is limping",
    "a person wearing a helmet and an orange vest fell to the ground",
    "a person wearing a helmet and an orange vest is sitting",
    "a person wearing a helmet and an orange vest is riding motocycle"
  ],
  threshold: 21,
  skip_frames: true,
  num_of_skip_frames: 5,
  confidence_threshold: 0.25,
  top_k: 5,
  batch_size: 32,
  frame_sample_rate: 4,
  processing_mode: "sequential"
};

const ExperimentsPage: React.FC = () => {
  const [results, setResults] = useState<ExperimentResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [request, setRequest] = useState<UBnormalExperimentRequest>(defaultRequest);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const runExperiment = async () => {
    // Start loading and send request to backend
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/experiments/ubnormal/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request)
      });
      if (!response.ok) throw new Error("Failed to fetch experiment results");
      const data = await response.json();
      setResults(data.statistics);
    } catch (error) {
      console.error("❌ Error fetching experiment results:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = () => {
    if (!results) return;
    // Prepare data for saving and trigger download
    const fullData = { request_data: request, result_data: results };
    const filename = `experiment_results_${new Date().toISOString().replace(/[:.]/g, "_")}.json`;
    const blob = new Blob([JSON.stringify(fullData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.download = filename;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="experiments-container">
      {/* Navigation bar with controls */}
      <header className="experiments-navbar">
        <h1 className="app-title">🧪 Experiments Dashboard</h1>
        <div className="navbar-buttons">
          <button className="button set-parameters-button" onClick={() => setIsModalOpen(true)}>⚙️ Set Parameters</button>
          <button className="button save-config-button" onClick={handleSave} disabled={!results}>💾 Save Results</button>
          <button className="button start-button" onClick={runExperiment} disabled={loading}>🚀 Run</button>
        </div>
      </header>

      {/* Loading overlay shown while experiment is running */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <p className="loading-text">Running experiments...</p>
        </div>
      )}

      {/* Show results and charts if experiment has finished */}
      {results && !loading && (
        <div className="experiments-content">
          <div className="results-grid">
            <div className="result-block"><strong>True Positives:</strong> {results.true_positives}</div>
            <div className="result-block"><strong>False Positives:</strong> {results.false_positives}</div>
            <div className="result-block"><strong>False Negatives:</strong> {results.false_negatives}</div>
            <div className="result-block"><strong>Precision:</strong> {results.precision.toFixed(2)}</div>
            <div className="result-block"><strong>Recall:</strong> {results.recall.toFixed(2)}</div>
            <div className="result-block"><strong>F1 Score:</strong> {results.f1_score.toFixed(2)}</div>
          </div>

          <div className="charts-section">
            {/* Bar chart for detection counts */}
            <div className="chart-box">
              <Bar
                data={{
                  labels: ["True Positives", "False Positives", "False Negatives"],
                  datasets: [{
                    label: "Detection Counts",
                    data: [results.true_positives, results.false_positives, results.false_negatives],
                    backgroundColor: ["#28a745", "#dc3545", "#ffc107"]
                  }]
                }}
                options={{ responsive: true, plugins: { legend: { display: false } } }}
              />
            </div>

            {/* Bar chart for precision/recall/F1 */}
            <div className="chart-box">
              <Bar
                data={{
                  labels: ["Precision", "Recall", "F1 Score"],
                  datasets: [{
                    label: "Score",
                    data: [results.precision, results.recall, results.f1_score],
                    backgroundColor: ["#4caf50", "#2196f3", "#ff9800"]
                  }]
                }}
                options={{
                  responsive: true,
                  indexAxis: 'y',
                  plugins: { legend: { display: false } },
                  scales: { x: { min: 0, max: 1, ticks: { stepSize: 0.1 } } }
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ExperimentParamsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onApply={(newParams) => {
          setRequest(newParams);
          setIsModalOpen(false);
        }}
        existingRequest={request}
      />
    </div>
  );
};

export default ExperimentsPage;
