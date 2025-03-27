import React, { useState, useEffect } from "react";
import "./CategoryModal.css"; // Import CSS súboru

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUseCategories: (categories: string[]) => void;
  existingCategories?: string[]; // 🔥 Pridali sme tento prop
}

const CategoryModal: React.FC<CategoryModalProps> = ({ isOpen, onClose, onUseCategories, existingCategories }) => {
  const [jsonText, setJsonText] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string>("No file selected");

  // ✅ Keď modal dostane nové kategórie, zobrazíme ich v `jsonText`
  useEffect(() => {
    if (isOpen && existingCategories && existingCategories.length > 0) {
      setJsonText(JSON.stringify(existingCategories, null, 2)); // Formátované JSON
    }
  }, [isOpen, existingCategories]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFileName(file.name);
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

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 className="modal-title">📂 Category List</h2>

        {/* ✅ Zobrazíme kategórie v JSON formáte */}
        <textarea
          className="modal-textarea"
          rows={6}
          placeholder='Enter categories as JSON (e.g. ["cat1", "cat2"])'
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
        />

        {/* Minimalistický input na súbor */}
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
