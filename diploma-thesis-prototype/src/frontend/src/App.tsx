import { useState } from "react";
import FirstScreen from "./FirstScreen";
import SecondScreen from "./SecondScreen";
import RunningAnalysisScreen from "./RunningAnalysisScreen";
import "./App.css";

interface Stage {
  name: string;
  status: "pending" | "in-progress" | "done";
}

const App: React.FC = () => {
  const [screen, setScreen] = useState<"first" | "running" | "second">("first");
  const [categories, setCategories] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any> | null>(null);
  const [stages, setStages] = useState<Stage[]>([
    { name: "Upload", status: "pending" },
    { name: "Detection", status: "pending" },
    { name: "Preprocess", status: "pending" },
    { name: "Recognition", status: "pending" },
    { name: "Interpreter", status: "pending" },
    { name: "Visualization", status: "pending" },
  ]);

  const updateStageStatus = (stageName: string, status: "pending" | "in-progress" | "done") => {
    setStages((prevStages) => {
      const updated = prevStages.map((stage) =>
        stage.name === stageName ? { ...stage, status } : stage
      );
      if (stageName === "visualization" && status === "done") {
        setTimeout(() => setScreen("second"), 1000);
      }
      return updated;
    });
  };

  if (screen === "first") {
    return (
      <FirstScreen
        setCategories={setCategories}
        setSettings={setSettings}
        startRunningAnalysis={() => setScreen("running")}
        updateStageStatus={updateStageStatus}
      />
    );
  }

  if (screen === "running") {
    return <RunningAnalysisScreen stages={stages} />;
  }

  return <SecondScreen categoriesFromFirstScreen={categories} settingsFromFirstScreen={settings} />;
};

export default App;
