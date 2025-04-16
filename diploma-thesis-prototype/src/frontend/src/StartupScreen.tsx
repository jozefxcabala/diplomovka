import React, { useState } from "react";
import styles from "./StartupScreen.module.css";
import LoadConfigModal from "./components/LoadConfigModal";
import LoadAnalysisModal from "./components/LoadAnalysisModal";

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

interface StartupScreenProps {
  onStartNewAnalysis?: () => void;
  onLoadConfig?: (config: ConfigItem) => void;
  onViewResults?: (video: AnalyzedVideo) => void;
}

const StartupScreen: React.FC<StartupScreenProps> = ({
  onStartNewAnalysis,
  onLoadConfig,
  onViewResults
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isResultModalOpen, setIsResultModalOpen] = useState(false);

  const handleSelectConfig = (config: ConfigItem) => {
    setIsModalOpen(false);
    onLoadConfig?.(config);
  };

  const handleResultSelect = (video: AnalyzedVideo) => {
    setIsResultModalOpen(false);
    onViewResults?.(video);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>🎥 Welcome to the Prototype</h1>
      <p className={styles.subtitle}>Choose how you'd like to proceed</p>

      <div className={styles.options}>
        <div className={styles.card}>
          <h2>🆕 New Analysis</h2>
          <p>Upload video, configure settings and categories</p>
          <button onClick={onStartNewAnalysis}>Start Fresh</button>
        </div>

        <div className={styles.card}>
          <h2>📄 Load Configuration</h2>
          <p>Select a previously saved configuration to continue</p>
          <button onClick={() => setIsModalOpen(true)}>Load Config</button>
        </div>

        <div className={styles.card}>
          <h2>💾 View Existing Results</h2>
          <p>View results from a previously analyzed video</p>
          <button onClick={() => setIsResultModalOpen(true)}>View Results</button>
        </div>
      </div>

      <LoadConfigModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelect={handleSelectConfig}
      />

      <LoadAnalysisModal
        isOpen={isResultModalOpen}
        onClose={() => setIsResultModalOpen(false)}
        onSelect={handleResultSelect}
      />
    </div>
  );
};

export default StartupScreen;