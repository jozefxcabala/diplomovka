import { useState, useEffect, useRef } from "react";
import "./App.css"; // Import CSS styles
import "./components/VideoInput.css";
import DetectionsView from "./components/DetectionsView";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import { time } from "node:console";

interface Detection {
  id: string;
  timestamp: number;
  confidence: number;
  isAnomaly: boolean;
  typeOfAnomaly: string;
}
interface SecondScreenProps {
  categoriesFromFirstScreen: string[];
  settingsFromFirstScreen: Record<string, any> | null;
  videoId: number;
}

const SecondScreen: React.FC<SecondScreenProps> = ({ categoriesFromFirstScreen, settingsFromFirstScreen, videoId }) => {
  const [categories, setCategories] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any> | null>([]);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [isBottomPanelOpen, setIsBottomPanelOpen] = useState<boolean>(false);
  const [isAnalysisCompleted, setIsAnalysisCompleted] = useState<boolean>(false);
  const [outputVideoPath, setOutputVideoPath] = useState<string>("");
  const [videoError, setVideoError] = useState<boolean>(false);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [fps, setFPS] = useState<number>(1);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);

  const isAnalysisReady = categories.length > 0 && settings !== null;

  useEffect(() => {
    setOutputVideoPath(`http://localhost:8001/output/${videoId}/final_output.mp4`);
    setIsAnalysisCompleted(true);

    const fetchVideoData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/video/${videoId}`);
        if (!response.ok) {
          throw new Error("Video not found");
        }
        const data = await response.json();
        setFPS(data.fps);
      } catch (error) {
        console.error("Failed to fetch video data:", error);
      }
    };

    const fetchDetections = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/detections/${videoId}`);
        const data = await res.json();
        const formatted = data.detections
          .filter((det: any) => det.is_anomaly === true) 
          .map((det: any) => ({
            id: det.id.toString(),
            timestamp: det.start_frame,
            confidence: det.confidence || 1.0,
            isAnomaly: det.is_anomaly,
            typeOfAnomaly: det.type_of_anomaly
          }));
        setDetections(formatted);
      } catch (err) {
        console.error("❌ Failed to fetch detections:", err);
      }
    };
    fetchVideoData();
    fetchDetections();
  }, [videoId]);

  useEffect(() => {
    setCategories(categoriesFromFirstScreen);
    setSettings(settingsFromFirstScreen);
  }, [categoriesFromFirstScreen, settingsFromFirstScreen]);

  const startAnalysis = () => {
    if (!isAnalysisReady) return;

    console.log("🔍 Starting analysis with the following parameters:");
    console.log("📌 Categories:", categories);
    console.log("⚙️ Settings:", settings);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsBottomPanelOpen(false);
      }
    };

    if (isBottomPanelOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isBottomPanelOpen]);

  const toggleBottomPanel = () => {
    setIsBottomPanelOpen((prev) => !prev);
  };

  const handleDetectionClick = (timestamp: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timestamp / fps;
      // videoRef.current.play(); // Automaticky spustí video
    }
  };

  return (
    <div className="app-container">
      {/* Top navigation bar */}
      <nav className="navbar">
        <h1 className="app-title">🎥 The Prototype</h1>
        <div className="navbar-buttons">
          <button className="button category-button" onClick={() => setIsCategoryModalOpen(true)}>
            📂 Change Categories
          </button>
          <button className="button settings-button" onClick={() => setIsSettingsModalOpen(true)}>
            ⚙️ Change Configuration
          </button>
          <button
            className={`button start-button ${isAnalysisReady ? "enabled" : "disabled"}`}
            onClick={startAnalysis}
            disabled={!isAnalysisReady}
          >
            🚀 Run Analysis
          </button>
        </div>
      </nav>
  
      {/* Main Content */}
      <div className="main-content">
          {isAnalysisCompleted ? (
            <div className="video-container">
              {videoError ? (
                <p className="error-message">⚠️ Video file not found. Please check the server.</p>
              ) : (
                <video
                  ref={videoRef}
                  className="video-preview"
                  width={window.innerWidth}
                  height={window.innerHeight - 128}
                  controls
                  src={outputVideoPath}
                  onError={() => setVideoError(true)}
                />
              )}
            </div>
          ) : (
            <div className="analysis-screen">
              <h2>🔍 Analysis in Progress...</h2>
              <p>Processing the video...</p>
            </div>
          )}
      </div>
  
      {/* Clickable Bottom Panel */}
      <div ref={panelRef} className={`bottom-panel ${isBottomPanelOpen ? "open" : "closed"}`} onClick={toggleBottomPanel}>
        <div className="panel-drag-bar"></div>
        {isBottomPanelOpen ? <div className="detection-header">Hide Detections 🔥</div> : <div className="detection-header">Show Detections 🔥</div>}
        {isBottomPanelOpen && (
          <div className="panel-content">
            <DetectionsView detections={detections} onDetectionClick={handleDetectionClick} fps={fps}/>
          </div>
        )}
      </div>
  
      {/* Modals */}
      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onUseCategories={(selectedCategories: string[]) => {
          setCategories(selectedCategories);
          setIsCategoryModalOpen(false);
        }}
        existingCategories={categories} // 🔥 Teraz modal dostane už existujúce kategórie
      />
  
      <PrototypeSettingModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        onUseSettings={(loadedSettings: Record<string, any>) => {
          setSettings(loadedSettings);
          setIsSettingsModalOpen(false);
        }}
        existingSettings={settings}
      />
    </div>
  );
};

export default SecondScreen;