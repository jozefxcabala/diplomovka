/**
 * SaveConfigButton component
 *
 * This button allows users to save the current analysis configuration (settings + categories) to the backend.
 *
 * Props:
 * - categories: list of selected category labels
 * - settings: object containing current analysis settings
 * - disabled: whether the button is disabled
 * - buttonText: optional label for the button
 * - onSaved: optional callback triggered with configId after successful save
 *
 * On click:
 * - Prompts the user to enter a name for the configuration.
 * - Sends a POST request to the backend API to save the config.
 * - Displays a success alert and triggers the `onSaved` callback if provided.
 */
import React from "react";

interface SaveConfigButtonProps {
  categories: string[];
  settings: Record<string, any> | null;
  disabled?: boolean;
  buttonText?: string;
  onSaved?: (configId: number) => void;
}

const SaveConfigButton: React.FC<SaveConfigButtonProps> = ({
  categories,
  settings,
  disabled,
  buttonText = "💾 Save Configuration",
  onSaved
}) => {
  const handleClick = async () => {
    if (!categories || !settings) return;

    const name = prompt("Enter name for the configuration:");
    if (!name) return;

    try {
      const response = await fetch("http://localhost:8000/api/configuration", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, categories, settings }),
      });

      if (!response.ok) throw new Error("Failed to save configuration");

      const data = await response.json();
      alert(`✅ Configuration saved!`);
      if (onSaved) onSaved(data.config_id);
    } catch (err: any) {
      console.error("❌ Error saving configuration:", err);
      alert(`Failed to save: ${err.message}`);
    }
  };

  return (
    <button className="button save-config-button" onClick={handleClick} disabled={disabled}>
      {buttonText}
    </button>
  );
};

export default SaveConfigButton;
