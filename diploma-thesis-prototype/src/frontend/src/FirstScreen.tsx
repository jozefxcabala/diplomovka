import { useState, useEffect } from "react";
import VideoInput from "./components/VideoInput";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import "./App.css"; 
import SaveConfigButton from "./components/SaveConfigurationButton";

interface FirstScreenProps {
  categories?: string[];
  settings?: Record<string, any> | null;
  setCategories: (categories: string[]) => void;
  setSelectedCategoryFileName: (selectedFileName: string) => void;
  setSelectedSettingsFileName: (selectedFileName: string) => void;
  setVideoId: (videoId: number) => void;
  setSettings: (settings: Record<string, any>) => void;
  startRunningAnalysis: () => void;
  updateStageStatus: (stageKey: string, status: "pending" | "in-progress" | "done") => void;
  goToStartupScreen: () => void;
}

const FirstScreen: React.FC<FirstScreenProps> = ({
  categories,
  settings,
  setCategories,
  setSettings,
  setVideoId,
  startRunningAnalysis,
  updateStageStatus,
  setSelectedCategoryFileName,
  setSelectedSettingsFileName,
  goToStartupScreen
}) => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [categoriesFirstScreen, setCategoriesFirstScreen] = useState<string[]>([]);
  const [settingsFirstScreen, setSettingsFirstScreen] = useState<Record<string, any> | null>(null);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight);

  useEffect(() => {
    const handleResize = () => setWindowHeight(window.innerHeight);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    categories && setCategoriesFirstScreen(categories);
    settings && setSettingsFirstScreen(settings);
  }, [categories, settings]);

  const isAnalysisReady = videoFile !== null && categoriesFirstScreen.length > 0 && settingsFirstScreen !== null;

  const startAnalysis = async () => {
    if (!isAnalysisReady || !videoFile || !settingsFirstScreen) return;

    const name_of_analysis = prompt("Enter name for the analysis:");
    if (!name_of_analysis) return;
  
    console.log("🔍 Starting analysis...");
    setCategories(categoriesFirstScreen);
    setSettings(settingsFirstScreen);
    startRunningAnalysis();
  
    try {
      // 1️⃣ Upload video
      console.log("📤 Uploading video...");
      updateStageStatus("Upload", "in-progress");
      const formData = new FormData();
      formData.append("video", videoFile);
  
      const uploadRes = await fetch("http://localhost:8000/api/video/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!uploadRes.ok) throw new Error("Video upload failed");
      const { video_path, video_filename }: { video_path: string, video_filename: string } = await uploadRes.json();
      updateStageStatus("Upload", "done");
      console.log("✅ Video uploaded. Name:", video_filename);
  
      // 2️⃣ Object Detection
      console.log("🧠 Running object detection...");
      updateStageStatus("Detection", "in-progress");
      const detectRes = await fetch("http://localhost:8000/api/object-detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_path,
          name_of_analysis,
          ...settingsFirstScreen,
        }),
      });
  
      if (!detectRes.ok) throw new Error("Object detection failed");
      const { video_id }: { video_id: number } = await detectRes.json();
      setVideoId(video_id);
      const output_path = `../data/output/${video_id}/anomaly_recognition_preprocessor`;
      updateStageStatus("Detection", "done");
      console.log("✅ Object detection complete.");

      // Save Configuration connected with running analysis
      console.log("🧠 Running save of configuration connected with analysis...");
      const config_name = `Config for first part of analysis video with id ${video_id}`;
      const configRes = await fetch("http://localhost:8000/api/configuration", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          name: config_name, 
          categories: categoriesFirstScreen, 
          settings: settingsFirstScreen 
        }),
      });

      if (!configRes.ok) throw new Error("Failed to save configuration");

      const data = await configRes.json();
      const config_id = data.config_id;

      const linkRes = await fetch("http://localhost:8000/api/configuration/link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id, config_id }),
      });

      if (!linkRes.ok) throw new Error("Failed to link configuration and analysis");

      console.log("✅ Saving configuration connected with analysis complete.");
  
      // 3️⃣ Anomaly Preprocessing
      console.log("⚙️ Running anomaly preprocessing...");
      updateStageStatus("Preprocess", "in-progress");
      const preprocRes = await fetch("http://localhost:8000/api/anomaly/preprocess", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_path,
          video_id,
          output_path,
          processing_mode: settingsFirstScreen.processing_mode
        }),
      });
  
      if (!preprocRes.ok) throw new Error("Anomaly preprocessing failed");
      updateStageStatus("Preprocess", "done");
      console.log("✅ Anomaly preprocessing complete.");
  
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
          categories: categoriesFirstScreen,
          batch_size: settingsFirstScreen.batch_size,
          frame_sample_rate: settingsFirstScreen.frame_sample_rate,
          processing_mode: settingsFirstScreen.processing_mode
        }),
      });
  
      if (!recogRes.ok) throw new Error("Anomaly recognition failed");
      updateStageStatus("Recognition", "done");
      console.log("🎉 Anomaly recognition complete!");
  
      // 5 Result Interpreter
      console.log("🔎 Running result interpretation...");
      updateStageStatus("Interpreter", "in-progress");
      const threshold = settingsFirstScreen?.threshold;
      const resIntRes = await fetch("http://localhost:8000/api/result-interpreter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id,
          threshold,
          categories: categoriesFirstScreen
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
  

  return (
    <div className="app-container">
      <nav className="navbar">
        <h1 className="app-title">🎥 The Prototype</h1>
        <div className="navbar-buttons">
          <button className="button home-button" onClick={goToStartupScreen}>
            🏠 Home
          </button>
          <button className="button category-button" onClick={() => setIsCategoryModalOpen(true)} disabled={!videoFile}>
            📂 Select Categories
          </button>
          <button className="button settings-button" onClick={() => setIsSettingsModalOpen(true)} disabled={!videoFile}>
            ⚙️ Set Configuration
          </button>
          <SaveConfigButton
            categories={categoriesFirstScreen}
            settings={settingsFirstScreen}
            disabled={!isAnalysisReady}
          />
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
          setCategoriesFirstScreen(selectedCategories);
          setIsCategoryModalOpen(false);
        }}
        setSelectedCategoryFileName={setSelectedCategoryFileName}
        existingCategories={categoriesFirstScreen}
      />

      <PrototypeSettingModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        onUseSettings={(loadedSettings: Record<string, any>) => {
          setSettingsFirstScreen(loadedSettings);
          setIsSettingsModalOpen(false);
        }}
        setSelectedSettingsFileName={setSelectedSettingsFileName}
        existingSettings={settingsFirstScreen}
      />
    </div>
  );
};

export default FirstScreen;
