/**
 * DetectionsView component
 *
 * Displays a list of detection results from a video analysis.
 * Each detection can be clicked to seek to the corresponding timestamp in the video.
 *
 * Props:
 * - detections: array of detection objects with id, timestamp, confidence, and anomalies
 * - onDetectionClick: callback to jump to the detection timestamp in the video
 * - fps: frames per second used to convert timestamp to seconds
 *
 * Features:
 * - Displays the top anomaly label per detection (by score)
 * - Highlights timestamp and ID for each detection
 */
import React from "react";
import "./DetectionsView.css"; 

interface Detection {
  id: string;
  timestamp: number;
  confidence: number;
  anomalies: {
    label: string;
    score: number;
  }[];
}

interface DetectionViewProps {
  detections: Detection[];
  onDetectionClick: (timestamp: number) => void;
  fps: number;
}

const DetectionsView: React.FC<DetectionViewProps> = ({ detections, onDetectionClick, fps }) => {
  return (
    <div className="detection-view">
      {detections.map((detection) => {
        // Select the top-scoring anomaly for display
        const topAnomaly = detection.anomalies.length > 0
          ? detection.anomalies.reduce((best, current) =>
              current.score > best.score ? current : best
            )
          : null;

        return (
          // Clicking the item triggers a jump to the video timestamp
          <div key={detection.id} className="detection-item" onClick={() => onDetectionClick(detection.timestamp)}>
            <div className="detection-info">
              <h3 className="detection-title">
                {topAnomaly ? `${topAnomaly.label}` : "No anomaly"}
              </h3>
              <p className="detection-id">ID: {detection.id}</p>
              <p className="detection-time">Time: {Math.floor(detection.timestamp / fps)}s</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DetectionsView;