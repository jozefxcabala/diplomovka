import React, { useEffect, useState } from "react";
import "./LoadConfigModal.css";
import FlipCard from "./FlipCard";

interface ConfigItem {
  id: number;
  name: string;
  categories: string[];
  settings: Record<string, any>;
}

interface LoadConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (config: ConfigItem) => void;
}

const LoadConfigModal: React.FC<LoadConfigModalProps> = ({ isOpen, onClose, onSelect }) => {
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

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
    try {
      await fetch(`http://localhost:8000/api/configuration/${id}`, { method: "DELETE" });
      setConfigs((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      alert("Failed to delete configuration.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="config-modal-overlay">
      <div className="config-modal-content">
        <h2>📄 Select Configuration</h2>

        {error && <p className="error">{error}</p>}

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

        <button onClick={onClose} className="close-button">Cancel</button>
      </div>
    </div>
  );
};

export default LoadConfigModal;