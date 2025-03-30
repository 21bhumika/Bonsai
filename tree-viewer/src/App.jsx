import React, { useState } from "react";
import "./App.css";

function App() {
  const [images, setImages] = useState([]);
  const [running, setRunning] = useState(false);

  const startGeneration = () => {
    setImages([]);
    setRunning(true);
  
    const es = new EventSource("http://localhost:5000/run-main");
    let count = 0;
  
    es.onmessage = (event) => {
      const filename = event.data;
      setImages(prev => [...prev, `http://localhost:5000/output/${filename}`]);
  
      count++;
      if (count >= 5) {
        es.close();
        setRunning(false);
      }
    };
  
    es.onerror = (err) => {
      console.error("EventSource failed:", err);
      es.close();
      setRunning(false);
    };
  };

  return (
    <div className="app">
      <h1>🌲 Live Tree Generator</h1>
      <button onClick={startGeneration} disabled={running}>
        {running ? "Generating..." : "Generate Trees"}
      </button>
      <div className="gallery">
        {images.map((src, idx) => (
          <img key={idx} src={src} alt={`tree-${idx}`} width="200" />
        ))}
      </div>
    </div>
  );
}

export default App;
