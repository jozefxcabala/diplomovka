import React, { useRef, useState } from "react";
import { FaPlay } from "react-icons/fa";
import "./VideoInput.css";

interface VideoInputProps {
  width?: number;
  height?: number;
  onVideoUpload: (file: File | null) => void;
}

const VideoInput: React.FC<VideoInputProps> = ({ width = 640, height = 360, onVideoUpload }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [source, setSource] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setSource(url);
      onVideoUpload(file);
    }
  };

  const handleChoose = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  return (
    <div className="video-input">
      <input
        ref={inputRef}
        className="video-input-hidden"
        type="file"
        onChange={handleFileChange}
        accept=".mp4"
        hidden
      />
      {!source && (
        <button className="upload-button" onClick={handleChoose}>
          <span className="upload-icon">
            <FaPlay />
          </span>
          <span className="upload-text">Upload video</span>
        </button>
      )}
      {source && (
        <video className="video-preview" width={width} height={height} controls src={source} />
      )}
    </div>
  );
};

export default VideoInput;
