import React, { useEffect, useState } from "react";

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
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      const mockData: ExperimentResults = {
        total_detections: 150,
        true_positives: 120,
        false_positives: 20,
        false_negatives: 10,
        precision: 120 / (120 + 20),
        recall: 120 / (120 + 10),
        f1_score: 2 * (120 / (120 + 20)) * (120 / (120 + 10)) / ((120 / (120 + 20)) + (120 / (120 + 10)))
      };
  
      setResults(mockData);
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <div className="experiments-page">
      <h1>📊 Experiment Results</h1>
      {loading && <p>Running experiments...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {results && (
        <div className="experiment-results">
          <p><strong>Total Detections:</strong> {results.total_detections}</p>
          <p><strong>True Positives:</strong> {results.true_positives}</p>
          <p><strong>False Positives:</strong> {results.false_positives}</p>
          <p><strong>False Negatives:</strong> {results.false_negatives}</p>
          <p><strong>Precision:</strong> {results.precision.toFixed(2)}</p>
          <p><strong>Recall:</strong> {results.recall.toFixed(2)}</p>
          <p><strong>F1 Score:</strong> {results.f1_score.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
};

export default ExperimentsPage;