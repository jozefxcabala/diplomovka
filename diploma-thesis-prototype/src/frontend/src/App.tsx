import { useState, useEffect, useRef } from "react";
import VideoInput from "./components/VideoInput";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import "./App.css"; // Import CSS styles
import DetectionsView from "./components/DetectionsView";

const detections = [
  {
    id: "123",
    type: "Person",
    timestamp: "12:45:10",
    probability: 0.98,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "124",
    type: "Car",
    timestamp: "12:46:20",
    probability: 0.85,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "125",
    type: "Bike",
    timestamp: "12:47:30",
    probability: 0.75,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "126",
    type: "Dog",
    timestamp: "12:48:45",
    probability: 0.92,
    imageUrl: "https://placehold.co/50x50",
  },
  {
    id: "127",
    type: "Fire",
    timestamp: "12:50:10",
    probability: 0.99,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "123",
    type: "Person",
    timestamp: "12:45:10",
    probability: 0.98,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "124",
    type: "Car",
    timestamp: "12:46:20",
    probability: 0.85,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "125",
    type: "Bike",
    timestamp: "12:47:30",
    probability: 0.75,
    imageUrl: "https://placehold.co/50x50"
  },
  {
    id: "126",
    type: "Dog",
    timestamp: "12:48:45",
    probability: 0.92,
    imageUrl: "https://placehold.co/50x50",
  },
  {
    id: "127",
    type: "Fire",
    timestamp: "12:50:10",
    probability: 0.99,
    imageUrl: "https://placehold.co/50x50"
  },
];

const App: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any> | null>(null);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [isAnalysisRunning, setIsAnalysisRunning] = useState<boolean>(false);
  const [isBottomPanelOpen, setIsBottomPanelOpen] = useState<boolean>(false);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  const panelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

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

  const isAnalysisReady = videoFile !== null && categories.length > 0 && settings !== null;

  const startAnalysis = () => {
    if (!isAnalysisReady) return;

    console.log("🔍 Starting analysis with the following parameters:");
    console.log("🎥 Video:", videoFile?.name);
    console.log("📌 Categories:", categories);
    console.log("⚙️ Settings:", settings);

    setIsAnalysisRunning(true);
    setIsBottomPanelOpen(true);
  };

  const toggleBottomPanel = () => {
    setIsBottomPanelOpen((prev) => !prev);
  };

  const handleSelectClick = () => {
    console.log("Select");
  };

  return (
    <div className="app-container">
      {/* Top navigation bar */}
      <nav className="navbar">
        <h1 className="app-title">🎥 The Prototype</h1>
        <div className="navbar-buttons">
          <button className="button category-button" onClick={() => setIsCategoryModalOpen(true)} disabled={!videoFile}>
            📂 Change Categories
          </button>
          <button className="button settings-button" onClick={() => setIsSettingsModalOpen(true)} disabled={!videoFile}>
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
        {false ? (
          <div className="video-container">
            <VideoInput width={window.innerWidth} height={windowHeight - 64} onVideoUpload={setVideoFile} />
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
            <DetectionsView detections={detections} />
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
      />

      <PrototypeSettingModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        onUseSettings={(loadedSettings: Record<string, any>) => {
          setSettings(loadedSettings);
          setIsSettingsModalOpen(false);
        }}
      />
    </div>
  );
};

export default App;
