import React, { useEffect, useState } from "react";
import "./LoadAnalysisModal.css";

interface ConfigItem {
  id: number;
  name: string;
  categories: string[];
  settings: Record<string, any>;
}

interface AnalyzedVideo {
  id: number;
  video_path: string;
  duration: number;
  fps: number;
  date_processed: string;
  name_of_analysis: string;
  config: ConfigItem;
}
interface LoadAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (video: AnalyzedVideo) => void;
}

const LoadAnalysisModal: React.FC<LoadAnalysisModalProps> = ({ isOpen, onClose, onSelect }) => {
  const [results, setResults] = useState<AnalyzedVideo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    const fetchResults = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/results/xclip-preprocessing");
        if (!res.ok) throw new Error("Failed to fetch results");
        const data = await res.json();
        setResults(data);
      } catch (err) {
        setError("Error loading results.");
      }
    };
    fetchResults();
  }, [isOpen]);

  const handleDelete = async (id: number) => {
    await fetch(`http://localhost:8000/api/results/xclip-preprocessing/${id}`, { method: "DELETE" });
    setResults((prev) => prev.filter((c) => c.id !== id));
  };

  if (!isOpen) return null;

  return (
    <div className="config-modal-overlay">
      <div className="config-modal-content">
        <h2>📼 Select Previous Analysis</h2>
        {error && <p className="error">{error}</p>}

        <div className="config-list-wrapper">
          <ul className="config-list">
            {results?.map((video) => (
              <li key={video.id} className="config-item">
              <div
                className="result-card"
                onClick={() => onSelect(video)}
              >
                <div className="result-details">
                  <strong title={video.name_of_analysis}>
                    {video.name_of_analysis.length > 30
                      ? `${video.name_of_analysis.slice(0, 30)}...`
                      : video.name_of_analysis}
                  </strong>
                  <p title={video.video_path}>
                    <span>📁</span>{" "}
                    {video.video_path.length > 40
                      ? `${video.video_path.slice(0, 40)}...`
                      : video.video_path}
                  </p>
                  <p><span>⏱️</span> {video.duration}s | {video.fps}fps</p>
                  <p><span>📅</span> {new Date(video.date_processed).toLocaleString()}</p>
                </div>
                <div className="result-actions">
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(video.id);
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
            ))}
          </ul>
        </div>

        <div className="config-footer">
          <button className="footer-button cancel" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default LoadAnalysisModal;