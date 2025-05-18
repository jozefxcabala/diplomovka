/**
 * LoadConfigModal component
 *
 * This modal allows users to:
 * - Select an existing configuration and load it for use.
 * - Switch to editing mode to modify or delete configurations in YAML format.
 *
 * Features:
 * - Fetches configurations from the backend on open.
 * - Displays configurations in flip card format with use and delete actions.
 * - Provides a YAML editor for modifying selected configurations.
 * - Validates YAML content before saving changes back to the backend.
 *
 * Props:
 * - isOpen: boolean that controls modal visibility
 * - onClose: function to close the modal
 * - onSelect: function called when a configuration is selected for use
 */
import React, { useEffect, useState } from "react";
import yaml from "js-yaml";
import FlipCard from "./FlipCard";
import "./LoadConfigModal.css";

interface ConfigItem {
  id: number;
  name: string;
  categories: string[];
  settings: Record<string, any>;
  created_at: string;
}

interface LoadConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (config: ConfigItem) => void;
}

// Validates the structure and types of the configuration object
const validateConfig = (config: any): string[] => {
  const errors: string[] = [];

  const expectedTopKeys: { [key: string]: string } = {
    name: "string",
    categories: "object",
    settings: "object",
    id: "number",
    created_at: "string",
  };

  const expectedSettingsKeys: { [key: string]: string } = {
    threshold: "number",
    model_path: "string",
    num_segments: "number",
    processing_mode: "string",
    classes_to_detect: "object",
  };

  for (const key in expectedTopKeys) {
    if (!(key in config)) {
      errors.push(`Missing key: '${key}'`);
    } else if (typeof config[key] !== expectedTopKeys[key]) {
      errors.push(`'${key}' should be of type ${expectedTopKeys[key]}`);
    }
  }

  if (typeof config.settings === "object") {
    for (const key in expectedSettingsKeys) {
      if (!(key in config.settings)) {
        errors.push(`Missing key: 'settings.${key}'`);
      } else if (typeof config.settings[key] !== expectedSettingsKeys[key]) {
        errors.push(`'settings.${key}' should be of type ${expectedSettingsKeys[key]}`);
      }
    }
  }

  return errors;
};

const LoadConfigModal: React.FC<LoadConfigModalProps> = ({ isOpen, onClose, onSelect }) => {
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isEditingMode, setIsEditingMode] = useState<boolean>(false);
  const [editingConfigId, setEditingConfigId] = useState<number | null>(null);
  const [yamlText, setYamlText] = useState<string>("");

  useEffect(() => {
    if (!isOpen) return;
    // Fetch configurations from backend when modal is opened
    const fetchConfigs = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/configuration");
        const data = await res.json();
        setConfigs(data);
      } catch (err) {
        setError("Failed to load configurations.");
      }
    };
    fetchConfigs();
  }, [isOpen]);

  const handleDelete = async (id: number) => {
    await fetch(`http://localhost:8000/api/configuration/${id}`, { method: "DELETE" });
    // Optimistically remove config from state after delete
    setConfigs((prev) => prev.filter((c) => c.id !== id));
  };

  const handleEditClick = (config: ConfigItem) => {
    // Prepare selected config for YAML editing
    setEditingConfigId(config.id);
    setYamlText(yaml.dump(config));
    setError(null);
  };

  const handleCancelEdit = () => {
    setEditingConfigId(null);
    setIsEditingMode(false);
    setYamlText("");
    setError(null);
  };

  const handleSaveChanges = async () => {
    // Parse and validate YAML text before saving
    try {
      const parsed = yaml.load(yamlText) as ConfigItem;

      const validationErrors = validateConfig(parsed);
      if (validationErrors.length > 0) {
        setError("Validation failed:\n" + validationErrors.join("\n"));
        return;
      }

      await fetch(`http://localhost:8000/api/configuration/${parsed.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });

      setEditingConfigId(null);
      setIsEditingMode(false);
      setError(null);

      // Refresh configuration list after successful update
      const res = await fetch("http://localhost:8000/api/configuration");
      const updated = await res.json();
      setConfigs(updated);
    } catch (err) {
      setError("YAML parsing or saving failed.");
    }
  };

  // Hide modal if not open
  if (!isOpen) return null;

  return (
    <div className="config-modal-overlay">
      <div className="config-modal-content">
        <h2>📄 Select Configuration</h2>

        {error && <pre className="error">{error}</pre>}

        {/* View: selection mode */}
        {!isEditingMode ? (
          <>
            <div className="config-list-wrapper">
              <ul className="config-list">
                {configs.map((config) => (
                  <li key={config.id} className="config-item">
                    <FlipCard
                      config={config}
                      onUse={() => onSelect(config)}
                      onDelete={() => handleDelete(config.id)}
                    />
                  </li>
                ))}
              </ul>
            </div>

            <div className="config-footer">
              <button className="footer-button cancel" onClick={onClose}>Cancel</button>
              <button className="footer-button edit" onClick={() => setIsEditingMode(true)}>Edit Configurations</button>
            </div>
          </>
        ) : 
        /* View: choose config to edit */
        editingConfigId === null ? (
          <>
            <div className="config-list-wrapper">
              <ul className="config-list">
                {configs.map((config) => (
                  <li key={config.id} className="config-item">
                    <div className="clickable-config" onClick={() => handleEditClick(config)}>
                      <FlipCard config={config} onUse={() => {}} onDelete={() => {}} />
                    </div>
                  </li>
                ))}
              </ul>
            </div>

            <div className="config-footer">
              <button className="footer-button cancel" onClick={handleCancelEdit}>Cancel</button>
            </div>
          </>
        ) : 
        /* View: editing YAML of selected config */
        (
          <>
            <textarea
              value={yamlText}
              onChange={(e) => setYamlText(e.target.value)}
              rows={20}
              className="config-edit-area"
            />
            <div className="config-footer">
              <button className="footer-button cancel" onClick={handleCancelEdit}>Cancel</button>
              <button className="footer-button save" onClick={handleSaveChanges}>Save Changes</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LoadConfigModal;