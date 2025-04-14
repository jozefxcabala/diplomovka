import { useState } from "react";
import "./FlipCard.css";

interface ConfigItem {
  id: number;
  name: string;
  categories: string[];
  settings: Record<string, any>;
}

interface FlipCardProps {
  config: ConfigItem;
  onUse: () => void;
  onDelete: () => void;
}

const FlipCard: React.FC<FlipCardProps> = ({ config, onUse, onDelete }) => {
  const [flipped, setFlipped] = useState(false);

  return (
    <div className={`flip-card ${flipped ? "flipped" : ""}`}>
      <div className="flip-card-inner">
        {/* Front side */}
        <div className="flip-card-front">
          <div className="flip-header">
            <strong className="config-name">{config.name}</strong>
            <div className="config-actions">
              <button className="use" onClick={onUse}>Use</button>
              <button className="delete" onClick={onDelete}>Delete</button>
              <button className="info" onClick={() => setFlipped(true)}>Show Info</button>
            </div>
          </div>
        </div>

        {/* Back side */}
        <div className="flip-card-back">
        <div className="back-info">
          <div className="config-categories">
            {config.categories.map((cat, idx) => (
              <span key={idx} className="category-badge">{cat}</span>
            ))}
          </div>
          <div className="config-meta">
            <span>Model: {config.settings.model_path.split("/").pop()}</span>
            <span>Threshold: {config.settings.threshold}</span>
            <span>Segments: {config.settings.num_segments}</span>
          </div>
        </div>

        <div className="config-actions">
          <button className="info" onClick={() => setFlipped(false)}>Hide Info</button>
        </div>
      </div>
      </div>
    </div>
  );
};

export default FlipCard;