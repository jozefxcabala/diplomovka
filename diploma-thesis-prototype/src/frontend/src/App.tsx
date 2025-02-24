import { useState, useEffect } from "react";
import "./App.css"; // Import CSS styles
import FirstScreen from "./FirstScreen";
import SecondScreen from "./SecondScreen";

const App: React.FC = () => {
  const [isAnalysisRunning, setIsAnalysisRunning] = useState<boolean>(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [settings, setSettings] = useState<Record<string, any> | null>(null);

  return isAnalysisRunning ? (
    <SecondScreen categoriesFromFirstScreen={categories} settingsFromFirstScreen={settings} />
  ) : (
    <FirstScreen
      setIsAnalysisRunning={setIsAnalysisRunning}
      setCategories={setCategories}
      setSettings={setSettings}
    />
  );
};

export default App;
