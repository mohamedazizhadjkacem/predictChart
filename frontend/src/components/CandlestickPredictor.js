import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import axios from 'axios';
import styled from 'styled-components';
import ImageUploader from './ImageUploader';
import PredictionResult from './PredictionResult';
import ProcessingSteps from './ProcessingSteps';
import LoadingSpinner from './LoadingSpinner';

const Container = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  color: #333;
`;

const Title = styled.h2`
  color: #4A90E2;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: 600;
`;

const StatusMessage = styled.div`
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  background: ${props => {
    switch (props.type) {
      case 'success': return '#d4edda';
      case 'error': return '#f8d7da';
      case 'info': return '#d1ecf1';
      default: return '#e2e3e5';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'success': return '#155724';
      case 'error': return '#721c24';
      case 'info': return '#0c5460';
      default: return '#383d41';
    }
  }};
  border: 1px solid ${props => {
    switch (props.type) {
      case 'success': return '#c3e6cb';
      case 'error': return '#f5c6cb';
      case 'info': return '#bee5eb';
      default: return '#d1d3d4';
    }
  }};
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20px;
`;

const Button = styled.button`
  background: ${props => props.variant === 'secondary' ? '#6c757d' : '#4A90E2'};
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.variant === 'secondary' ? '#5a6268' : '#357abd'};
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const CandlestickPredictor = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [processSteps, setProcessSteps] = useState([]);

  // Configure axios base URL
  const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? '/api'  // In production, use relative path
    : 'http://localhost:8000';  // In development, use direct backend URL

  const axiosConfig = {
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 second timeout
  };

  const addProcessStep = (step, status = 'running') => {
    setProcessSteps(prev => [...prev, { step, status, timestamp: new Date() }]);
    setCurrentStep(step);
  };

  const updateLastStep = (status) => {
    setProcessSteps(prev => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1].status = status;
      }
      return updated;
    });
  };

  const resetProcess = () => {
    setUploadedFile(null);
    setUploadedImageUrl(null);
    setPredictionResult(null);
    setIsProcessing(false);
    setCurrentStep('');
    setProcessSteps([]);
  };

  const handleFileUpload = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please upload an image file');
        return;
      }

      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB');
        return;
      }

      setUploadedFile(file);
      
      // Create preview URL
      const imageUrl = URL.createObjectURL(file);
      setUploadedImageUrl(imageUrl);
      
      toast.success('Image uploaded successfully!');
      
      // Reset previous results
      setPredictionResult(null);
      setProcessSteps([]);
    }
  }, []);

  const processFullPipeline = async () => {
    if (!uploadedFile) {
      toast.error('Please upload an image first');
      return;
    }

    setIsProcessing(true);
    setProcessSteps([]);
    
    try {
      addProcessStep('Uploading image to backend...');
      
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await axios.post('/full-process', formData, {
        ...axiosConfig,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Important for image response
      });

      updateLastStep('completed');
      addProcessStep('Processing complete! Displaying result...', 'completed');

      // Create blob URL for the result image
      const imageBlob = new Blob([response.data], { type: 'image/png' });
      const resultImageUrl = URL.createObjectURL(imageBlob);
      
      setPredictionResult({
        imageUrl: resultImageUrl,
        timestamp: new Date(),
        originalFile: uploadedFile.name
      });

      toast.success('Prediction completed successfully!');

    } catch (error) {
      console.error('Error processing image:', error);
      updateLastStep('error');
      
      let errorMessage = 'Failed to process image';
      if (error.response?.data) {
        try {
          const errorText = await error.response.data.text();
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = 'Network error occurred';
        }
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      }
      
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
      setCurrentStep('');
    }
  };

  const processStepByStep = async () => {
    if (!uploadedFile) {
      toast.error('Please upload an image first');
      return;
    }

    setIsProcessing(true);
    setProcessSteps([]);
    
    try {
      // Step 1: Convert image to numeric
      addProcessStep('Converting image to numeric data...');
      
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const numericResponse = await axios.post('/convert-image-to-numeric', formData, {
        ...axiosConfig,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      updateLastStep('completed');
      const numericData = numericResponse.data.numeric;
      
      // Step 2: Get prediction
      addProcessStep(`Sending ${numericData.length} candlesticks to AI service...`);
      
      const predictionResponse = await axios.post('/predict', {
        numeric: numericData
      }, axiosConfig);

      updateLastStep('completed');
      const prediction = predictionResponse.data.future;
      
      // Step 3: Reconstruct image
      addProcessStep(`Reconstructing ${prediction.length} predicted candlesticks to image...`);
      
      const reconstructResponse = await axios.post('/reconstruct-image', {
        numeric: prediction
      }, {
        ...axiosConfig,
        responseType: 'blob',
      });

      updateLastStep('completed');
      addProcessStep('Process completed!', 'completed');

      // Create blob URL for the result
      const imageBlob = new Blob([reconstructResponse.data], { type: 'image/png' });
      const resultImageUrl = URL.createObjectURL(imageBlob);
      
      setPredictionResult({
        imageUrl: resultImageUrl,
        timestamp: new Date(),
        originalFile: uploadedFile.name,
        numericData,
        prediction,
        stepByStep: true
      });

      toast.success('Step-by-step processing completed!');

    } catch (error) {
      console.error('Error in step-by-step processing:', error);
      updateLastStep('error');
      
      const errorMessage = error.response?.data?.detail || 'Processing failed';
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
      setCurrentStep('');
    }
  };

  return (
    <Container>
      <Card>
        <Title>📁 Upload Candlestick Chart</Title>
        <ImageUploader 
          onFileUpload={handleFileUpload}
          uploadedImageUrl={uploadedImageUrl}
          isProcessing={isProcessing}
        />
        
        {uploadedFile && (
          <ButtonGroup>
            <Button 
              onClick={processFullPipeline}
              disabled={isProcessing}
            >
              🚀 Full Pipeline Prediction
            </Button>
            <Button 
              variant="secondary"
              onClick={processStepByStep}
              disabled={isProcessing}
            >
              🔍 Step-by-Step Process
            </Button>
            <Button 
              variant="secondary"
              onClick={resetProcess}
              disabled={isProcessing}
            >
              🔄 Reset
            </Button>
          </ButtonGroup>
        )}
      </Card>

      {isProcessing && (
        <Card>
          <Title>⚙️ Processing</Title>
          <LoadingSpinner />
          {currentStep && (
            <StatusMessage type="info">
              <strong>Current Step:</strong> {currentStep}
            </StatusMessage>
          )}
          <ProcessingSteps steps={processSteps} />
        </Card>
      )}

      {predictionResult && (
        <Card>
          <Title>🎯 Prediction Result</Title>
          <PredictionResult result={predictionResult} />
        </Card>
      )}
    </Container>
  );
};

export default CandlestickPredictor;