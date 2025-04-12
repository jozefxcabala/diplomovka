import React from "react";
import "./DetectionsView.css"; 
interface Detection {
  id: string;
  timestamp: number;
  confidence: number;
  isAnomaly: boolean;
  typeOfAnomaly: string;
}

interface DetectionViewProps {
  detections: Detection[];
  onDetectionClick: (timestamp: number) => void;
  fps: number;
}

const DetectionsView: React.FC<DetectionViewProps> = ({ detections, onDetectionClick, fps }) => {
  return (
    <div className="detection-view">
      {detections.map((detection) => (
        <div key={detection.id} className="detection-item" onClick={() => onDetectionClick(detection.timestamp)}>
          <div className="detection-info">
            <h3 className="detection-title">{detection.typeOfAnomaly}</h3>
            <p className="detection-id">ID: {detection.id}</p>
            <p className="detection-time">Time: {Math.floor(detection.timestamp / fps)}s</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DetectionsView;
