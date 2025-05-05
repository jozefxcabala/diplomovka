import React, { useEffect, useState } from "react";
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

const ExperimentsPage: React.FC = () => {
  const [results, setResults] = useState<ExperimentResults | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchExperimentResults = async () => {
      setLoading(true);
      try {
        const response = await fetch("http://localhost:8000/api/experiments/ubnormal/run", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            "dataset_path": "/Users/caby/annotation-app/UBnormal",
            "model_path": "/Users/caby/diplomovka/diploma-thesis-prototype/data/models/yolo11n.pt",
            "num_segments": 8,
            "categories": [
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
            "threshold": 21,
            "skip_frames": true,
            "num_of_skip_frames": 5,
            "confidence_threshold": 0.25
          })
        });
  
        if (!response.ok) {
          throw new Error("Failed to fetch experiment results");
        }
  
        const data = await response.json();
        const statistics: ExperimentResults = data.statistics
        setResults(statistics);
      } catch (error) {
        console.error("❌ Error fetching experiment results:", error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchExperimentResults();
  }, []);

  const handleSave = () => {
    if (!results) return;

    const filename = `experiment_results_${new Date().toISOString().replace(/[:.]/g, "_")}.json`;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.download = filename;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="experiments-container"><p>Running experiments...</p></div>;

  return (
    <div className="experiments-container">
      <header className="experiments-navbar">
        <h1 className="app-title">🧪 Experiments Dashboard</h1>
        <div className="navbar-buttons">
          <button className="button save-config-button" onClick={handleSave}>💾 Save Results</button>
        </div>
      </header>

      {results && (
        <div className="experiments-content">
          <div className="results-grid">
            <div className="result-block"><strong>Total Detections:</strong> {results.total_detections}</div>
            <div className="result-block"><strong>True Positives:</strong> {results.true_positives}</div>
            <div className="result-block"><strong>False Positives:</strong> {results.false_positives}</div>
            <div className="result-block"><strong>False Negatives:</strong> {results.false_negatives}</div>
            <div className="result-block"><strong>Precision:</strong> {results.precision.toFixed(2)}</div>
            <div className="result-block"><strong>Recall:</strong> {results.recall.toFixed(2)}</div>
            <div className="result-block"><strong>F1 Score:</strong> {results.f1_score.toFixed(2)}</div>
          </div>

          <div className="charts-section">
            <div className="chart-box">
              <Bar
                data={{
                  labels: ["True Positives", "False Positives", "False Negatives"],
                  datasets: [
                    {
                      label: "Detection Counts",
                      data: [results.true_positives, results.false_positives, results.false_negatives],
                      backgroundColor: ["#28a745", "#dc3545", "#ffc107"]
                    }
                  ]
                }}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { display: false }
                  }
                }}
              />
            </div>

            <div className="chart-box">
              <Bar
                data={{
                  labels: ["Precision", "Recall", "F1 Score"],
                  datasets: [
                    {
                      label: "Score",
                      data: [results.precision, results.recall, results.f1_score],
                      backgroundColor: ["#4caf50", "#2196f3", "#ff9800"]
                    }
                  ]
                }}
                options={{
                  responsive: true,
                  indexAxis: 'y',
                  plugins: {
                    legend: { display: false }
                  },
                  scales: {
                    x: {
                      min: 0,
                      max: 1,
                      ticks: {
                        stepSize: 0.1
                      }
                    }
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExperimentsPage;