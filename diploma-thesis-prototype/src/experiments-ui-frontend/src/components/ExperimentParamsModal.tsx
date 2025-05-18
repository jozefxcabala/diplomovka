/**
 * ExperimentParamsModal component
 *
 * A modal interface for editing experiment parameters in YAML format.
 * This component is used to configure how the experiment is executed.
 *
 * Props:
 * - isOpen: controls the visibility of the modal
 * - onClose: function to close the modal
 * - onApply: callback triggered with the parsed experiment settings
 * - existingRequest: the current experiment configuration to prefill the editor
 *
 * Features:
 * - Loads the existing experiment request and serializes it as YAML
 * - Allows the user to modify the YAML
 * - Validates YAML input before applying the configuration
 */
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
  batch_size: number;
  frame_sample_rate: number;
  processing_mode: string;
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

  // Load and serialize the existing request when modal opens
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

  // Parse YAML input and apply settings if valid
  const handleApply = () => {
    try {
      const parsed = yaml.load(yamlText) as ExperimentRequest;
      onApply(parsed);
      onClose();
    } catch (err) {
      setError("❌ Invalid YAML format. Please correct it.");
    }
  };

  // Don’t render modal when it's closed
  if (!isOpen) return null;

  // Modal content and layout
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
