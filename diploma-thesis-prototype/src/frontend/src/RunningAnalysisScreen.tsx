import React from "react";
import styles from "./RunningAnalysisScreen.module.css";

interface Stage {
  name: string;
  status: "pending" | "in-progress" | "done";
}

interface RunningAnalysisScreenProps {
  stages: Stage[];
}

const RunningAnalysisScreen: React.FC<RunningAnalysisScreenProps> = ({ stages }) => {
  return (
    <div className={styles.container}>
      {stages.map((stage, index) => (
        <div key={index} className={`${styles.stageBox} ${styles[stage.status]}`}>
          <span className={styles.stageText}>{stage.name}</span>
        </div>
      ))}
    </div>
  );
};

export default RunningAnalysisScreen;
