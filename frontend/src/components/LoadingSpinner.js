import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
`;

const Spinner = styled.div`
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4A90E2;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: 20px;
`;

const LoadingText = styled.div`
  font-size: 1.1rem;
  color: #4A90E2;
  font-weight: 500;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingSubtext = styled.div`
  font-size: 0.9rem;
  color: #666;
  margin-top: 10px;
  text-align: center;
  max-width: 300px;
`;

const LoadingSpinner = ({ message = "Processing your image...", subtext = "This may take a few moments while our AI analyzes your candlestick chart." }) => {
  return (
    <SpinnerContainer>
      <Spinner />
      <LoadingText>{message}</LoadingText>
      <LoadingSubtext>{subtext}</LoadingSubtext>
    </SpinnerContainer>
  );
};

export default LoadingSpinner;