import React from 'react';
import styled from 'styled-components';

const StepsContainer = styled.div`
  margin-top: 20px;
`;

const Step = styled.div`
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    border-bottom: none;
  }
`;

const StepIcon = styled.div`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  
  background: ${props => {
    switch (props.status) {
      case 'completed': return '#28a745';
      case 'error': return '#dc3545';
      case 'running': return '#007bff';
      default: return '#6c757d';
    }
  }};
  
  color: white;
`;

const StepContent = styled.div`
  flex: 1;
`;

const StepText = styled.div`
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
`;

const StepTime = styled.div`
  font-size: 0.8rem;
  color: #666;
`;

const getStepIcon = (status) => {
  switch (status) {
    case 'completed': return '✓';
    case 'error': return '✗';
    case 'running': return '⟳';
    default: return '○';
  }
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
};

const ProcessingSteps = ({ steps }) => {
  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <StepsContainer>
      <h4 style={{ marginBottom: '15px', color: '#333' }}>Processing Steps:</h4>
      
      {steps.map((step, index) => (
        <Step key={index}>
          <StepIcon status={step.status}>
            {getStepIcon(step.status)}
          </StepIcon>
          
          <StepContent>
            <StepText>{step.step}</StepText>
            <StepTime>{formatTime(step.timestamp)}</StepTime>
          </StepContent>
        </Step>
      ))}
    </StepsContainer>
  );
};

export default ProcessingSteps;