import { useState, useEffect } from "react";
import VideoInput from "./components/VideoInput";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import "./App.css"; // Import CSS styles

interface FirstScreenProps {
  setIsAnalysisRunning: (value: boolean) => void;
  setCategories: (categories: string[]) => void;
  setSettings: (settings: Record<string, any>) => void;
}

const FirstScreen: React.FC<FirstScreenProps> = ({
  setIsAnalysisRunning,
  setCategories,
  setSettings
}) => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [categories, updateCategories] = useState<string[]>([]);
  const [settings, updateSettings] = useState<Record<string, any> | null>(null);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const isAnalysisReady = videoFile !== null && categories.length > 0 && settings !== null;

  const startAnalysis = () => {
    if (!isAnalysisReady) return;

    console.log("🔍 Starting analysis with the following parameters:");
    console.log("🎥 Video:", videoFile?.name);
    console.log("📌 Categories:", categories);
    console.log("⚙️ Settings:", settings);

    setCategories(categories); // Posielame do App.tsx
    setSettings(settings); // Posielame do App.tsx
    setIsAnalysisRunning(true); // Prepne na SecondScreen
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <h1 className="app-title">🎥 The Prototype</h1>
        <div className="navbar-buttons">
          <button className="button category-button" onClick={() => setIsCategoryModalOpen(true)} disabled={!videoFile}>
            📂 Select Categories
          </button>
          <button className="button settings-button" onClick={() => setIsSettingsModalOpen(true)} disabled={!videoFile}>
            ⚙️ Set Configuration
          </button>
          <button
            className={`button start-button ${isAnalysisReady ? "enabled" : "disabled"}`}
            onClick={startAnalysis}
            disabled={!isAnalysisReady}
          >
            🚀 Start Analysis
          </button>
        </div>
      </nav>

      <div className="video-container">
        <VideoInput width={window.innerWidth} height={windowHeight - 64} onVideoUpload={setVideoFile} />
      </div>

      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        onUseCategories={(selectedCategories: string[]) => {
          updateCategories(selectedCategories);
          setIsCategoryModalOpen(false);
        }}
      />

      <PrototypeSettingModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        onUseSettings={(loadedSettings: Record<string, any>) => {
          updateSettings(loadedSettings);
          setIsSettingsModalOpen(false);
        }}
      />
    </div>
  );
};

export default FirstScreen;
