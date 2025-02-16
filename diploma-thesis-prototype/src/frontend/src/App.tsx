import { useState, useEffect } from "react";
import VideoInput from "./components/VideoInput";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import "./App.css"; // Import CSS styles

const App: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any> | null>(null);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  // Maintain the correct video height when resizing the window
  useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Condition to enable the "Start Analysis" button
  const isAnalysisReady = videoFile !== null && categories.length > 0 && settings !== null;

  // Function to start the analysis
  const startAnalysis = () => {
    if (!isAnalysisReady) return;

    console.log("🔍 Starting analysis with the following parameters:");
    console.log("🎥 Video:", videoFile?.name);
    console.log("📌 Categories:", categories);
    console.log("⚙️ Settings:", settings);

    // Here you can add a fetch/axios request to the backend (e.g., POST to an API endpoint)
  };

  return (
    <div className="app-container">
      {/* Top navigation bar */}
      <nav className="navbar">
        <h1 className="app-title">🎥 The Prototype</h1>
        <div className="navbar-buttons">
          <button
            className="button category-button"
            onClick={() => setIsCategoryModalOpen(true)}
            disabled={!videoFile}
            title={
              videoFile
                ? "Click to select categories for searching"
                : "❌ You must upload a video before clicking this button"
            }
          >
            📂 Select Categories
          </button>
          <button
            className="button settings-button"
            onClick={() => setIsSettingsModalOpen(true)}
            disabled={!videoFile}
            title={
              videoFile
                ? "Click to select settings to be used in the analysis"
                : "❌ You must upload a video before clicking this button"
            }
          >
            ⚙️ Set Configuration
          </button>
          <button
            className={`button start-button ${isAnalysisReady ? "enabled" : "disabled"}`}
            onClick={startAnalysis}
            disabled={!isAnalysisReady}
            title={
              isAnalysisReady
                ? "Click to start the analysis"
                : "❌ You must upload a video, select categories, and set configuration before starting the analysis"
            }
          >
            🚀 Start Analysis
          </button>
        </div>
      </nav>

      {/* Main panel for video playback */}
      <div className="video-container">
        <VideoInput width={window.innerWidth} height={windowHeight - 64} onVideoUpload={setVideoFile} />
      </div>

      {/* Category Modal */}
      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onUseCategories={(selectedCategories: string[]) => {
          setCategories(selectedCategories);
          setIsCategoryModalOpen(false);
        }}
      />

      {/* Prototype Setting Modal */}
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
