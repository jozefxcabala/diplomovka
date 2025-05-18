/**
 * PrototypeSettingModal component
 *
 * A modal component for configuring analysis settings in YAML format.
 *
 * Features:
 * - Textarea input for YAML-based setting customization
 * - File upload input to load settings from a `.yaml` file
 * - Button to load default settings
 * - Validation to check if YAML is correctly formatted
 *
 * Props:
 * - isOpen: controls whether the modal is visible
 * - onClose: closes the modal
 * - onUseSettings: callback that receives the parsed settings object
 * - existingSettings: optionally preload existing settings
 * - existingSelectedFileName: optionally display a previously selected file name
 * - setSelectedSettingsFileName: updates the file name in parent state
 */
import React, { useState, useEffect } from "react";
import yaml from "js-yaml";
import "./PrototypeSettingsModal.css";

interface PrototypeSettingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUseSettings: (settings: any) => void;
  existingSettings?: any;
  existingSelectedFileName?: string;
  setSelectedSettingsFileName?: (selectedFileName: string) => void;
}

const defaultYaml = `
###############################################
##            DO NOT CHANGE THIS             ##
###############################################
model_path: "data/models/yolo11n.pt"
batch_size: 32
frame_sample_rate: 4
num_segments: 8
processing_mode: "parallel"
classes_to_detect:
  - 0
skip_frames: true
num_of_skip_frames: 5
###############################################
##            YOU CAN CHANGE THIS            ##
###############################################
threshold: 22
confidence_threshold: 0.6
top_k: 1
`;

const PrototypeSettingModal: React.FC<PrototypeSettingModalProps> = ({
  isOpen,
  onClose,
  onUseSettings,
  existingSettings,
  existingSelectedFileName,
  setSelectedSettingsFileName,
}) => {
  const [yamlText, setYamlText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string>("No file chosen");

  useEffect(() => {
    if (isOpen && existingSettings) {
      try {
        const yamlString = yaml.dump(existingSettings);
        setYamlText(yamlString);
      } catch (err) {
        console.error("Failed to convert settings to YAML:", err);
      }
    }
  }, [isOpen, existingSettings]);

  useEffect(() => {
    if (isOpen && existingSelectedFileName) {
      setSelectedFileName(existingSelectedFileName);
    }
  }, [isOpen, existingSelectedFileName]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
      setSelectedSettingsFileName && setSelectedSettingsFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          yaml.load(text);
          setYamlText(text);
          setError(null);
        } catch (err) {
          setError("Invalid YAML format in file.");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleUseSettings = () => {
    try {
      const parsedSettings = yaml.load(yamlText);
      onUseSettings(parsedSettings);
      onClose();
    } catch (err) {
      setError("Invalid YAML format. Please enter a valid YAML.");
    }
  };

  const handleUseDefault = () => {
    setYamlText(defaultYaml);
    setSelectedFileName("Default loaded");
    setError(null);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">⚙️ Prototype Settings</h2>

        <textarea
          className="modal-textarea"
          rows={6}
          placeholder="Enter YAML settings here..."
          value={yamlText}
          onChange={(e) => setYamlText(e.target.value)}
        />

        <div className="modal-file-upload">
          <input type="file" id="actual-btn" hidden accept=".yaml,.yml" onChange={handleFileUpload} />
          <label htmlFor="actual-btn" className="file-label">Choose File</label>
          <span className="file-chosen">{selectedFileName}</span>
        </div>

        {error && <p className="modal-error">{error}</p>}

        <div className="modal-actions">
          <button onClick={onClose} className="modal-button close">Close</button>
          <button onClick={handleUseDefault} className="modal-button default">Use Default</button>
          <button onClick={handleUseSettings} className="modal-button confirm">Use Settings</button>
        </div>
      </div>
    </div>
  );
};

export default PrototypeSettingModal;