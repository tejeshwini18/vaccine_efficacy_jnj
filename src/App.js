import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [genderChart, setGenderChart] = useState('');
  const [ageChart, setAgeChart] = useState('');
  const [symptomChart, setSymptomChart] = useState('');
  const [dataDownloaded, setDataDownloaded] = useState(false);
  const [showGenderChart, setShowGenderChart] = useState(false);
  const [showAgeChart, setShowAgeChart] = useState(false);
  const [showSymptomChart, setShowSymptomChart] = useState(false);

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
      await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setStatus('File uploaded successfully. Processing data...');
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
        fetchCharts(); // Fetch charts after processing
      } else if (statusResponse.data.status === 'error') {
        setStatus('');
        setError('Error during data processing.');
      } else {
        setTimeout(checkProcessingStatus, 5000); // Retry after 5 seconds
      }
    } catch (error) {
      console.error('Processing status error:', error);
      setStatus('');
      setError('Error checking processing status: ' + error.message);
    }
  };

  const fetchCharts = async () => {
    const chartEndpoints = [
      { endpoint: 'gender-distribution', setter: setGenderChart, label: 'Gender' },
      { endpoint: 'age-distribution', setter: setAgeChart, label: 'Age' },
      { endpoint: 'symptom-distribution', setter: setSymptomChart, label: 'Symptom' },
    ];

    for (const { endpoint, setter, label } of chartEndpoints) {
      try {
        const response = await axios.get(`http://localhost:5000/${endpoint}`);
        if (response.data.error) {
          console.warn(`${label} chart error: ${response.data.error}`);
          setError(`Backend error for ${label} chart: ${response.data.error}`);
        } else {
          setter(`data:image/png;base64,${response.data.image}`);
        }
      } catch (error) {
        console.error(`Error fetching ${label} chart:`, error);
        if (error.response && error.response.status === 404) {
          setError(`Error fetching ${label} chart: Data not found. Make sure you uploaded and processed the file.`);
        } else {
          setError(`Error fetching ${label} chart: ${error.message}`);
        }
      }
    }
  };

  const downloadFile = async (fileType) => {
    try {
      const endpoint = fileType === 'Adverse' ? 'downloadAdverse' : 'downloadFiltered';
      const response = await axios.get(`http://localhost:5000/${endpoint}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${fileType}Effect.csv`);
      document.body.appendChild(link);
      link.click();
      setDataDownloaded(true);
      setStatus('Data downloaded successfully. You can now view the charts.');
    } catch (error) {
      console.error('Download error:', error);
      setError('Error downloading file: ' + error.message);
    }
  };

  const fetchSingleChart = async (endpoint, setter, label) => {
    try {
      const response = await axios.get(`http://localhost:5000/${endpoint}`);
      if (response.data.error) {
        console.warn(`${label} chart error: ${response.data.error}`);
        setError(`Backend error for ${label} chart: ${response.data.error}`);
      } else {
        setter(`data:image/png;base64,${response.data.image}`);
      }
    } catch (error) {
      console.error(`Error fetching ${label} chart:`, error);
      if (error.response && error.response.status === 404) {
        setError(`Error fetching ${label} chart: Data not found. Make sure you uploaded and processed the file.`);
      } else {
        setError(`Error fetching ${label} chart: ${error.message}`);
      }
    }
  };

  const handleGenderChart = () => {
    fetchSingleChart('gender-distribution', setGenderChart, 'Gender');
    setShowGenderChart(true);
    setShowAgeChart(false);
    setShowSymptomChart(false);
  };

  const handleAgeChart = () => {
    fetchSingleChart('age-distribution', setAgeChart, 'Age');
    setShowGenderChart(false);
    setShowAgeChart(true);
    setShowSymptomChart(false);
  };

  const handleSymptomChart = () => {
    fetchSingleChart('symptom-distribution', setSymptomChart, 'Symptom');
    setShowGenderChart(false);
    setShowAgeChart(false);
    setShowSymptomChart(true);
  };

  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '2rem',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f5f5f5',
      minHeight: '100vh'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '10px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '2rem'
      }}>
        <h1 style={{
          color: '#2c3e50',
          marginBottom: '1.5rem',
          textAlign: 'center',
          fontSize: '2.5rem'
        }}>Medical Data Analysis Dashboard</h1>

        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '1.5rem',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <input 
            type="file" 
            onChange={onFileChange}
            style={{
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              flex: '1',
              maxWidth: '400px'
            }}
          />
          <button 
            onClick={onFileUpload}
            style={{
              padding: '0.5rem 1.5rem',
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Upload
          </button>
        </div>

        {status && (
          <div style={{
            padding: '1rem',
            backgroundColor: '#e8f4f8',
            borderRadius: '4px',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            {status}
          </div>
        )}
        
        {error && (
          <div style={{
            padding: '1rem',
            backgroundColor: '#fde8e8',
            color: '#c53030',
            borderRadius: '4px',
            marginBottom: '1rem',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          marginBottom: '2rem'
        }}>
          <button
            onClick={() => downloadFile('Filtered')}
            disabled={!status.includes('Data processed') && !dataDownloaded}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#2ecc71',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              opacity: (!status.includes('Data processed') && !dataDownloaded) ? 0.5 : 1
            }}
          >
            Download Filtered Data
          </button>
          <button
            onClick={() => downloadFile('Adverse')}
            disabled={!status.includes('Data processed') && !dataDownloaded}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              opacity: (!status.includes('Data processed') && !dataDownloaded) ? 0.5 : 1
            }}
          >
            Download Adverse Data
          </button>
        </div>
      </div>

      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '10px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{
          color: '#2c3e50',
          marginBottom: '1.5rem',
          textAlign: 'center',
          fontSize: '2rem'
        }}>Data Visualization</h2>

        {!dataDownloaded ? (
          <div style={{ 
            padding: '1.5rem', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px',
            marginBottom: '1.5rem',
            textAlign: 'center'
          }}>
            <p style={{ margin: 0, color: '#666' }}>
              To view the visualization charts, please download the data first using the buttons above.
            </p>
          </div>
        ) : null}

        <div style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'center',
          marginBottom: '2rem',
          flexWrap: 'wrap'
        }}>
          <button 
            onClick={handleGenderChart}
            disabled={!dataDownloaded}
            style={{ 
              padding: '0.75rem 1.5rem',
              backgroundColor: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              opacity: dataDownloaded ? 1 : 0.6
            }}
          >
            Show Gender Distribution
          </button>
          <button 
            onClick={handleAgeChart}
            disabled={!dataDownloaded}
            style={{ 
              padding: '0.75rem 1.5rem',
              backgroundColor: '#9b59b6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              opacity: dataDownloaded ? 1 : 0.6
            }}
          >
            Show Age Distribution
          </button>
          <button 
            onClick={handleSymptomChart}
            disabled={!dataDownloaded}
            style={{ 
              padding: '0.75rem 1.5rem',
              backgroundColor: '#f1c40f',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold',
              opacity: dataDownloaded ? 1 : 0.6
            }}
          >
            Show Top Symptoms
          </button>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          marginTop: '2rem'
        }}>
          {showGenderChart && genderChart && (
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '1.5rem',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              width: '100%',
              maxWidth: '800px'
            }}>
              <h3 style={{
                color: '#2c3e50',
                marginBottom: '1rem',
                textAlign: 'center'
              }}>Gender Distribution</h3>
              <img 
                src={genderChart} 
                alt="Gender Distribution Chart" 
                style={{ 
                  width: '100%',
                  height: 'auto',
                  borderRadius: '4px'
                }} 
              />
            </div>
          )}
          {showAgeChart && ageChart && (
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '1.5rem',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              width: '100%',
              maxWidth: '800px'
            }}>
              <h3 style={{
                color: '#2c3e50',
                marginBottom: '1rem',
                textAlign: 'center'
              }}>Age Distribution</h3>
              <img 
                src={ageChart} 
                alt="Age Distribution Chart" 
                style={{ 
                  width: '100%',
                  height: 'auto',
                  borderRadius: '4px'
                }} 
              />
            </div>
          )}
          {showSymptomChart && symptomChart && (
            <div style={{
              backgroundColor: '#f8f9fa',
              padding: '1.5rem',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              width: '100%',
              maxWidth: '800px'
            }}>
              <h3 style={{
                color: '#2c3e50',
                marginBottom: '1rem',
                textAlign: 'center'
              }}>Top Symptoms</h3>
              <img 
                src={symptomChart} 
                alt="Top Symptoms Chart" 
                style={{ 
                  width: '100%',
                  height: 'auto',
                  borderRadius: '4px'
                }} 
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
