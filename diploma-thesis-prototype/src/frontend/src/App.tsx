/**
 * App component (main entry point)
 *
 * This component manages the overall screen flow and shared state of the application.
 * It determines which screen to display based on user actions:
 * - StartupScreen: initial screen for choosing to start, load config, or view results.
 * - FirstScreen: used to upload video, select categories and settings, and start full analysis.
 * - RunningAnalysisScreen: visualizes the progress of either full or partial analysis.
 * - SecondScreen: displays final analysis results and allows rerunning from selected stages.
 *
 * State includes:
 * - Screen selection (startup, first, running, partialRunning, second)
 * - Selected categories, settings, file names
 * - Video ID and loaded configuration
 * - Stage progress tracking for full or partial analysis
 */
import { useState } from "react";
import FirstScreen from "./FirstScreen";
import SecondScreen from "./SecondScreen";
import RunningAnalysisScreen from "./RunningAnalysisScreen";
import "./App.css";
import StartupScreen from "./StartupScreen";

interface Stage {
  name: string;
  status: "pending" | "in-progress" | "done";
}

const App: React.FC = () => {
  const [selectedCategoryFileName, setSelectedCategoryFileName] = useState<string>("");
  const [selectedSettingsFileName, setSelectedSettingsFileName] = useState<string>("");
  const [screen, setScreen] = useState<"startup" | "first" | "running" | "second" | "partialRunning">("startup");
  const [categories, setCategories] = useState<string[]>([]);
  const [videoId, setVideoId] = useState<number>(-1);
  const [settings, setSettings] = useState<Record<string, any> | null>(null);
  const [loadedConfig, setLoadedConfig] = useState<{ categories: string[]; settings: Record<string, any> } | null>(null);
  const [stages, setStages] = useState<Stage[]>([
    { name: "Upload", status: "pending" },
    { name: "Detection", status: "pending" },
    { name: "Preprocess", status: "pending" },
    { name: "Recognition", status: "pending" },
    { name: "Interpreter", status: "pending" },
    { name: "Visualization", status: "pending" },
  ]);
  const [partialStages, setPartialStages] = useState<Stage[]>([]);

  const resetStateAndGoHome = () => {
    setScreen("startup");
    setCategories([]);
    setSettings(null);
    setSelectedCategoryFileName("");
    setSelectedSettingsFileName("");
    setVideoId(-1);
    setLoadedConfig(null);
    setStages([
      { name: "Upload", status: "pending" },
      { name: "Detection", status: "pending" },
      { name: "Preprocess", status: "pending" },
      { name: "Recognition", status: "pending" },
      { name: "Interpreter", status: "pending" },
      { name: "Visualization", status: "pending" }
    ]);
    setPartialStages([]);
  };

  const updateStageStatus = (stageName: string, status: "pending" | "in-progress" | "done") => {
    setStages((prevStages) => {
      const updated = prevStages.map((stage) =>
        stage.name === stageName ? { ...stage, status } : stage
      );
      if (stageName === "Visualization" && status === "done") {
        setTimeout(() => setScreen("second"), 1000);
      }
      return updated;
    });

    setPartialStages((prevPartialStages) => {
      const updated = prevPartialStages.map((stage) =>
        stage.name === stageName ? { ...stage, status } : stage
      );
      if (stageName === "Visualization" && status === "done") {
        setTimeout(() => setScreen("second"), 1000);
      }
      return updated;
    });
  };

  const startPartialAnalysis = () => {
    setPartialStages([
      { name: "Recognition", status: "pending" },
      { name: "Interpreter", status: "pending" },
      { name: "Visualization", status: "pending" },
    ]);
    setScreen("partialRunning");
  };

  const onLoadConfig = (config: { categories: string[]; settings: Record<string, any> }) => {
    setLoadedConfig(config);
    setCategories(config.categories);
    setSettings(config.settings);
    setScreen("first");
  };

  const onViewResults = (video: any) => {
    setVideoId(video.id);
    setLoadedConfig(video.config);
    setCategories(video.config.categories);
    setSettings(video.config.settings);
    setScreen("second");
  };

  if (screen === "startup") {
    return ( <StartupScreen
      onStartNewAnalysis={() => setScreen("first")}
      onLoadConfig={onLoadConfig}
      onViewResults={onViewResults}
    />);
  }

  if (screen === "first") {
    return (
      <FirstScreen
        setVideoId={setVideoId}
        setCategories={setCategories}
        setSettings={setSettings}
        startRunningAnalysis={() => setScreen("running")}
        updateStageStatus={updateStageStatus}
        setSelectedCategoryFileName={setSelectedCategoryFileName}
        setSelectedSettingsFileName={setSelectedSettingsFileName}
        categories={categories}
        settings={settings}
        goToStartupScreen={resetStateAndGoHome}
      />
    );
  }

  if (screen === "running") {
    return <RunningAnalysisScreen stages={stages} />;
  }

  if (screen === "partialRunning") {
    return <RunningAnalysisScreen stages={partialStages} />;
  }

  return (
    <SecondScreen
      categories={categories}
      settings={settings}
      setCategories={setCategories}
      setSettings={setSettings}
      video_id={videoId}
      startRunningAnalysis={startPartialAnalysis}
      updateStageStatus={updateStageStatus}
      selectedCategoryFileName={selectedCategoryFileName}
      selectedSettingsFileName={selectedSettingsFileName}
      setSelectedCategoryFileName={setSelectedCategoryFileName}
      setSelectedSettingsFileName={setSelectedSettingsFileName}
      goToStartupScreen={resetStateAndGoHome}
    />
  );
};

export default App;
