/**
 * VideoInput component
 *
 * Allows the user to upload a .mp4 video file and preview it directly in the browser.
 * The video is passed back to the parent via the `onVideoUpload` callback.
 *
 * Props:
 * - width, height: dimensions of the preview video (default 640x360)
 * - onVideoUpload: function to handle the uploaded video file
 *
 * Features:
 * - Hidden file input triggered by a styled button
 * - Video preview shown once a file is selected
 */
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
