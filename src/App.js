import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [genderChart, setGenderChart] = useState('');
  const [ageChart, setAgeChart] = useState('');
  const [symptomChart, setSymptomChart] = useState('');

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
    setStatus('');
    setError('');
  };

  const onFileUpload = async () => {
    if (!file) {
      setError('No file selected.');
      return;
    }

    setStatus('Uploading file...');
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setStatus('File uploaded successfully. Processing data...');
      
      // Poll for processing status
      checkProcessingStatus();
    } catch (error) {
      console.error('Upload error:', error);
      setStatus('');
      setError('Error uploading file: ' + error.message);
    }
  };

  const checkProcessingStatus = async () => {
    setStatus('Processing data...');

    try {
      const statusResponse = await axios.get('http://localhost:5000/processing-status');

      if (statusResponse.data.status === 'completed') {
        setStatus('Data processed successfully. You can now download the results.');
        fetchCharts(); // Fetch charts once processing is complete
      } else if (statusResponse.data.status === 'error') {
        setStatus('');
        setError('Error during data processing.');
      } else {
        setTimeout(checkProcessingStatus, 5000); // Check every 5 seconds
      }
    } catch (error) {
      console.error('Processing status error:', error);
      setStatus('');
      setError('Error checking processing status: ' + error.message);
    }
  };

  const fetchCharts = async () => {
    try {
      const genderResponse = await axios.get('http://localhost:5000/gender-distribution');
      const ageResponse = await axios.get('http://localhost:5000/age-distribution');
      const symptomResponse = await axios.get('http://localhost:5000/symptom-distribution');

      setGenderChart(`data:image/png;base64,${genderResponse.data.image}`);
      setAgeChart(`data:image/png;base64,${ageResponse.data.image}`);
      setSymptomChart(`data:image/png;base64,${symptomResponse.data.image}`);
    } catch (error) {
      console.error('Error fetching charts:', error);
      setError('Error fetching charts: ' + error.message);
    }
  };

  const downloadFile = async (fileType) => {
    try {
      const response = await axios.get(`http://localhost:5000/download${fileType}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${fileType}.csv`);
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      console.error('Download error:', error);
      setError('Error downloading file: ' + error.message);
    }
  };

  return (
    <div>
      <h1>Medical Data Extraction</h1>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload</button>
      <div>
        {status && <p>Status: {status}</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>
      <div>
        <button 
          onClick={() => downloadFile('Filtered')} 
          disabled={status !== 'Data processed successfully. You can now download the results.'}
        >
          Download Filtered Data
        </button>
        <button 
          onClick={() => downloadFile('Adverse')} 
          disabled={status !== 'Data processed successfully. You can now download the results.'}
        >
          Download Adverse Data
        </button>
      </div>
      <div>
        {genderChart && <div>
          <h2>Gender Distribution</h2>
          <img src={genderChart} alt="Gender Distribution Chart" />
        </div>}
        {ageChart && <div>
          <h2>Age Distribution</h2>
          <img src={ageChart} alt="Age Distribution Chart" />
        </div>}
        {symptomChart && <div>
          <h2>Top Symptoms</h2>
          <img src={symptomChart} alt="Top Symptoms Chart" />
        </div>}
      </div>
    </div>
  );
}

export default App;
