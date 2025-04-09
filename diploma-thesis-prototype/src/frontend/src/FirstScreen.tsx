import { useState, useEffect } from "react";
import VideoInput from "./components/VideoInput";
import CategoryModal from "./components/CategoryModal";
import PrototypeSettingModal from "./components/PrototypeSettingsModal";
import "./App.css"; // Import CSS styles

interface FirstScreenProps {
  setCategories: (categories: string[]) => void;
  setVideoId: (videoId: number) => void;
  setSettings: (settings: Record<string, any>) => void;
  startRunningAnalysis: () => void;
  updateStageStatus: (stageKey: string, status: "pending" | "in-progress" | "done") => void;
}

const FirstScreen: React.FC<FirstScreenProps> = ({
  setCategories,
  setSettings,
  setVideoId,
  startRunningAnalysis,
  updateStageStatus,
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

  const startAnalysis = async () => {
    if (!isAnalysisReady || !videoFile || !settings) return;
  
    console.log("🔍 Starting analysis...");
    setCategories(categories);
    setSettings(settings);
    startRunningAnalysis();
  
    try {
      // 1️⃣ Upload video
      console.log("📤 Uploading video...");
      updateStageStatus("upload", "in-progress");
      const formData = new FormData();
      formData.append("video", videoFile);
  
      const uploadRes = await fetch("http://localhost:8000/api/video/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!uploadRes.ok) throw new Error("Video upload failed");
      const { video_path, video_filename }: { video_path: string, video_filename: string } = await uploadRes.json();
      updateStageStatus("upload", "done");
      console.log("✅ Video uploaded. Name:", video_filename);
  
      // 2️⃣ Object Detection
      console.log("🧠 Running object detection...");
      updateStageStatus("detection", "in-progress");
      const detectRes = await fetch("http://localhost:8000/api/object-detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_path,
          ...settings,
        }),
      });
  
      if (!detectRes.ok) throw new Error("Object detection failed");
      const { video_id }: { video_id: number } = await detectRes.json();
      setVideoId(video_id);
      const output_path = `../data/output/${video_id}/anomaly_recognition_preprocessor`;
      updateStageStatus("detection", "done");
      console.log("✅ Object detection complete.");
  
      // 3️⃣ Anomaly Preprocessing
      console.log("⚙️ Running anomaly preprocessing...");
      updateStageStatus("preprocess", "in-progress");
      const preprocRes = await fetch("http://localhost:8000/api/anomaly/preprocess", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_path,
          video_id,
          output_path
        }),
      });
  
      if (!preprocRes.ok) throw new Error("Anomaly preprocessing failed");
      updateStageStatus("preprocess", "done");
      console.log("✅ Anomaly preprocessing complete.");
  
      // 4️⃣ Anomaly Recognition
      console.log("🔎 Running anomaly recognition...");
      updateStageStatus("recognition", "in-progress");
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
      updateStageStatus("recognition", "done");
      console.log("🎉 Anomaly recognition complete!");
  
      // 5 Result Interpreter
      console.log("🔎 Running result interpretation...");
      updateStageStatus("interpreter", "in-progress");
      const threshold = settings?.threshold;
      console.log(threshold);
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
      updateStageStatus("interpreter", "done");
      console.log("🎉 Result interpretation complete!");

      // 6 Video Visualization
      console.log("🔎 Running video visualization...");
      updateStageStatus("visualization", "in-progress");
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
      updateStageStatus("visualization", "done");
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
