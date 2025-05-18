/**
 * RunningAnalysisScreen component
 *
 * This component displays the current progress of an analysis pipeline using a sequence of stages.
 *
 * Props:
 * - stages: An array of stage objects, each containing:
 *   - name: The name of the analysis stage.
 *   - status: One of 'pending', 'in-progress', or 'done', determining visual state.
 *
 * Each stage is displayed as a box, styled according to its current status.
 */
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
