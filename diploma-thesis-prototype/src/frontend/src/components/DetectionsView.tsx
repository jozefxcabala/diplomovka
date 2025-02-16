import React from "react";
import "./DetectionsView.css"; // Import CSS

interface Detections {
  id: string;
  type: string;
  timestamp: string;
  probability: number;
  imageUrl: string;
}

interface DetectionViewProps {
  detections: Detections[];
}

const DetectionsView: React.FC<DetectionViewProps> = ({ detections }) => {
  return (
    <div className="detection-panel">
      <div className="detection-view">
        {detections.map((detection) => (
          <div key={detection.id} className="detection-item">
            <img src={detection.imageUrl} alt="Detection" className="detection-image" />
            <div className="detection-info">
              <h3 className="detection-title">{detection.type}</h3>
              <p className="detection-id">ID: {detection.id}</p>
              <p className="detection-time">Time: {detection.timestamp}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DetectionsView;
