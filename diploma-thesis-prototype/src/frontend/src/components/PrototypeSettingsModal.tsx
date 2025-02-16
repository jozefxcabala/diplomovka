import React, { useState } from "react";
import yaml from "js-yaml";
import "./PrototypeSettingsModal.css"; // Import CSS súboru

interface PrototypeSettingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUseSettings: (settings: any) => void;
}

const PrototypeSettingModal: React.FC<PrototypeSettingModalProps> = ({ isOpen, onClose, onUseSettings }) => {
  const [yamlText, setYamlText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string>("No file chosen"); // Default text

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name); // Uloží názov vybraného súboru
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          yaml.load(text); // Overíme, či je to validný YAML
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

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">⚙️ Prototype Settings</h2>

        {/* Textarea na YAML konfiguráciu */}
        <textarea
          className="modal-textarea"
          rows={6}
          placeholder="Enter YAML settings here..."
          value={yamlText}
          onChange={(e) => setYamlText(e.target.value)}
        />

        {/* Upload YAML súboru */}
        <div className="modal-file-upload">
          <input type="file" id="actual-btn" hidden accept=".yaml,.yml" onChange={handleFileUpload} />
          <label htmlFor="actual-btn" className="file-label">Choose File</label>
          <span className="file-chosen">{selectedFileName}</span>
        </div>

        {/* Error hláška */}
        {error && <p className="modal-error">{error}</p>}

        <div className="modal-actions">
          <button onClick={onClose} className="modal-button close">Close</button>
          <button onClick={handleUseSettings} className="modal-button confirm">Use Settings</button>
        </div>
      </div>
    </div>
  );
};

export default PrototypeSettingModal;
