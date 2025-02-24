import React from "react";
import "./DetectionsView.css"; // Import CSS styles

interface Detections {
  id: string;
  type: string;
  timestamp: number;
  probability: number;
  imageUrl: string;
}

interface DetectionViewProps {
  detections: Detections[];
  onDetectionClick: (timestamp: number) => void;
}

const DetectionsView: React.FC<DetectionViewProps> = ({ detections, onDetectionClick }) => {
  return (
    <div className="detection-view">
      {detections.map((detection) => (
        <div key={detection.id} className="detection-item" onClick={() => onDetectionClick(detection.timestamp)}>
          <img src={detection.imageUrl} alt="Detection" className="detection-image" />
          <div className="detection-info">
            <h3 className="detection-title">{detection.type}</h3>
            <p className="detection-id">ID: {detection.id}</p>
            <p className="detection-time">Time: {detection.timestamp}s</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DetectionsView;
