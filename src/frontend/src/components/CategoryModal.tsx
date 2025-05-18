/**
 * CategoryModal component
 *
 * This modal allows users to define or load a list of categories used for analysis.
 *
 * Props:
 * - isOpen: controls modal visibility.
 * - onClose: closes the modal.
 * - onUseCategories: callback called with parsed category array.
 * - existingCategories: optional preloaded categories to display.
 * - existingSelectedFileName: optional previously selected filename.
 * - setSelectedCategoryFileName: callback to update selected file name.
 *
 * Features:
 * - Manually input JSON list of categories via a textarea.
 * - Load category list from a JSON file.
 * - Error handling for invalid JSON input.
 */
import React, { useState, useEffect } from "react";
import "./CategoryModal.css";

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUseCategories: (categories: string[]) => void;
  existingCategories?: string[];
  existingSelectedFileName?: string;
  setSelectedCategoryFileName?: (selectedFileName: string) => void;
}

const CategoryModal: React.FC<CategoryModalProps> = ({ isOpen, onClose, onUseCategories, existingCategories, existingSelectedFileName, setSelectedCategoryFileName}) => {
  const [jsonText, setJsonText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string>("No file selected");

  // Populate textarea with existing categories when modal opens
  useEffect(() => {
    if (isOpen && existingCategories && existingCategories.length > 0) {
      setJsonText(JSON.stringify(existingCategories, null, 2));
    }
  }, [isOpen, existingCategories]);

  // Load previously selected file name if available
  useEffect(() => {
    if (isOpen && existingSelectedFileName) {
      setSelectedFileName(existingSelectedFileName);
    }
  }, [isOpen, existingSelectedFileName]);

  // Handle loading category list from uploaded JSON file
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
      setSelectedCategoryFileName && setSelectedCategoryFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          JSON.parse(text);
          setJsonText(text);
          setError(null);
        } catch (err) {
          setError("Invalid JSON format in file.");
        }
      };
      reader.readAsText(file);
    }
  };

  // Parse and validate user input and trigger callback
  const handleUseCategories = () => {
    try {
      const parsedCategories = JSON.parse(jsonText);
      if (!Array.isArray(parsedCategories)) {
        throw new Error("JSON must be an array of categories.");
      }
      onUseCategories(parsedCategories);
      onClose();
    } catch (err) {
      setError("Invalid JSON format. Please enter a valid array.");
    }
  };

  // Do not render modal if it's not open
  if (!isOpen) return null;

  // Modal overlay and content
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">📂 Category List</h2>

        <textarea
          className="modal-textarea"
          rows={6}
          placeholder='Enter categories as JSON (e.g. ["cat1", "cat2"])'
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
        />

        <div className="modal-file-upload">
          <input id="actual-btn" type="file" accept=".json" onChange={handleFileUpload} hidden />
          <label htmlFor="actual-btn" className="file-label">Choose File</label>
          <span className="file-chosen">{selectedFileName}</span>
        </div>

        {error && <p className="modal-error">{error}</p>}

        <div className="modal-actions">
          <button onClick={onClose} className="modal-button close">Close</button>
          <button onClick={handleUseCategories} className="modal-button confirm">Use Category List</button>
        </div>
      </div>
    </div>
  );
};

export default CategoryModal;
