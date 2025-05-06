import React, { useState, useEffect } from "react";
import yaml from "js-yaml";
import "./ExperimentParamsModal.css";

interface ExperimentRequest {
  dataset_path: string;
  model_path: string;
  num_segments: number;
  categories: string[];
  threshold: number;
  skip_frames: boolean;
  num_of_skip_frames: number;
  confidence_threshold: number;
  top_k: number;
}

interface ExperimentParamsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (settings: ExperimentRequest) => void;
  existingRequest: ExperimentRequest;
}

const ExperimentParamsModal: React.FC<ExperimentParamsModalProps> = ({ isOpen, onClose, onApply, existingRequest }) => {
  const [yamlText, setYamlText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && existingRequest) {
      try {
        const yamlString = yaml.dump(existingRequest);
        setYamlText(yamlString);
      } catch (err) {
        console.error("Failed to convert settings to YAML:", err);
      }
    }
  }, [isOpen, existingRequest]);

  const handleApply = () => {
    try {
      const parsed = yaml.load(yamlText) as ExperimentRequest;
      onApply(parsed);
      onClose();
    } catch (err) {
      setError("❌ Invalid YAML format. Please correct it.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">⚙️ Experiment Parameters</h2>
        <textarea
          className="modal-textarea"
          rows={14}
          value={yamlText}
          onChange={(e) => setYamlText(e.target.value)}
        />
        {error && <p className="modal-error">{error}</p>}

        <div className="modal-actions">
          <button className="modal-button close" onClick={onClose}>Cancel</button>
          <button className="modal-button confirm" onClick={handleApply}>Apply</button>
        </div>
      </div>
    </div>
  );
};

export default ExperimentParamsModal;
