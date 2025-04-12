import { useState, useEffect, useRef } from "react";
import "./App.css"; // Import CSS styles
import "./components/VideoInput.css";
import DetectionsView from "./components/DetectionsView";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";

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
  video_id: number;
  startRunningAnalysis: () => void;
  updateStageStatus: (stageKey: string, status: "pending" | "in-progress" | "done") => void;
}

const SecondScreen: React.FC<SecondScreenProps> = ({ categoriesFromFirstScreen, settingsFromFirstScreen, video_id, startRunningAnalysis, updateStageStatus }) => {
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
    setOutputVideoPath(`http://localhost:8001/output/${video_id}/final_output.mp4`);
    setIsAnalysisCompleted(true);

    const fetchVideoData = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/video/${video_id}`);
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
        const res = await fetch(`http://localhost:8000/api/detections/${video_id}`);
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
  }, [video_id]);

  useEffect(() => {
    setCategories(categoriesFromFirstScreen);
    setSettings(settingsFromFirstScreen);
  }, [categoriesFromFirstScreen, settingsFromFirstScreen]);

  const rerunAnalysis = async () => {
    if (!isAnalysisReady) return;

    console.log("🔍 Rerun analysis with the following parameters:");
    console.log("📌 Categories:", categories);
    console.log("⚙️ Settings:", settings);
    setCategories(categories);
    setSettings(settings);

    startRunningAnalysis();
  
    try {
      // 4️⃣ Anomaly Recognition
      console.log("🔎 Running anomaly recognition...");
      updateStageStatus("Recognition", "in-progress");
      const recogRes = await fetch("http://localhost:8000/api/anomaly/recognition", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id,
          categories,
        }),
      });
  
      if (!recogRes.ok) throw new Error("Anomaly recognition failed");
      updateStageStatus("Recognition", "done");
      console.log("🎉 Anomaly recognition complete!");
  
      // 5 Result Interpreter
      console.log("🔎 Running result interpretation...");
      updateStageStatus("Interpreter", "in-progress");
      const threshold = settings?.threshold;
      const resIntRes = await fetch("http://localhost:8000/api/result-interpreter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id,
          threshold,
          categories
        }),
      });
  
      if (!resIntRes.ok) throw new Error("Result interpretation failed");
      updateStageStatus("Interpreter", "done");
      console.log("🎉 Result interpretation complete!");

      // 6 Video Visualization
      console.log("🔎 Running video visualization...");
      updateStageStatus("Visualization", "in-progress");
      const resVisRes = await fetch("http://localhost:8000/api/video/visualization", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id,
        }),
      });
  
      if (!resVisRes.ok) throw new Error("Video visualization failed");
      updateStageStatus("Visualization", "done");
      console.log("🎉 Video visualization complete!");
  
    } catch (error: unknown) {
      const err = error as Error;
      console.error("❌ Error during analysis:", err);
      alert(`Analysis failed: ${err.message}`);
    }
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
            onClick={rerunAnalysis}
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