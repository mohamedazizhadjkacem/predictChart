import React from 'react';
import styled from 'styled-components';

const ResultContainer = styled.div`
  text-align: center;
`;

const ResultImage = styled.img`
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
`;

const ResultInfo = styled.div`
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  text-align: left;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const InfoCard = styled.div`
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const InfoTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #4A90E2;
  font-size: 1rem;
`;

const InfoValue = styled.div`
  color: #333;
  font-weight: 500;
`;

const DownloadButton = styled.a`
  display: inline-block;
  background: #28a745;
  color: white;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  margin: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: #218838;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
`;

const DataSection = styled.div`
  margin-top: 20px;
  padding: 15px;
  background: #f1f3f4;
  border-radius: 8px;
`;

const DataTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
`;

const DataPreview = styled.div`
  background: white;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #ddd;
`;

const ToggleButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 10px;
  
  &:hover {
    background: #5a6268;
  }
`;

const PredictionResult = ({ result }) => {
  const [showRawData, setShowRawData] = React.useState(false);
  
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };
  
  // Check if we have image data or JSON data
  const hasImageData = result.imageUrl;
  const hasJsonData = result.originalData && result.predictions;

  const downloadImage = () => {
    const link = document.createElement('a');
    link.href = result.imageUrl;
    link.download = `prediction_${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatCandleData = (data) => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return 'No data available';
    }
    return data.map((candle, index) => 
      `${index + 1}: [O: ${candle[0]?.toFixed(4) || 'N/A'}, H: ${candle[1]?.toFixed(4) || 'N/A'}, L: ${candle[2]?.toFixed(4) || 'N/A'}, C: ${candle[3]?.toFixed(4) || 'N/A'}]`
    ).join('\n');
  };

  return (
    <ResultContainer>
      <div>
        <h3>🎯 Prediction Result: Original + Future Candlesticks</h3>
        {hasImageData && (
          <p>
            The image below shows your original candlestick chart (left) combined with 
            the AI-predicted future candlesticks (right).
          </p>
        )}
        {hasJsonData && (
          <p>
            The AI model has analyzed your candlestick data and generated predictions. 
            View the detailed results below.
          </p>
        )}
      </div>
      
      {hasImageData && (
        <ResultImage 
          src={result.imageUrl} 
          alt="Prediction result: Original + Future candlesticks"
          onClick={downloadImage}
          style={{ cursor: 'pointer' }}
          title="Click to download image"
        />
      )}
      
      {hasJsonData && !hasImageData && (
        <div style={{ 
          background: '#f8f9fa', 
          border: '2px dashed #4A90E2', 
          borderRadius: '10px', 
          padding: '30px', 
          margin: '20px 0',
          textAlign: 'center'
        }}>
          <h4 style={{ color: '#4A90E2', margin: '0 0 10px 0' }}>📊 Prediction Data Generated</h4>
          <p style={{ color: '#666', margin: '0' }}>AI analysis complete! View the detailed results below.</p>
        </div>
      )}
      
      <ResultInfo>
        <InfoGrid>
          <InfoCard>
            <InfoTitle>📅 Generated</InfoTitle>
            <InfoValue>{formatTimestamp(result.timestamp)}</InfoValue>
          </InfoCard>
          
          <InfoCard>
            <InfoTitle>📄 Original File</InfoTitle>
            <InfoValue>{result.originalFile}</InfoValue>
          </InfoCard>
          
          {result.stepByStep && (
            <InfoCard>
              <InfoTitle>🔍 Process Type</InfoTitle>
              <InfoValue>Step-by-Step Analysis</InfoValue>
            </InfoCard>
          )}
          
          {result.numericData && (
            <InfoCard>
              <InfoTitle>📊 Input Candles</InfoTitle>
              <InfoValue>{result.numericData.length} candlesticks</InfoValue>
            </InfoCard>
          )}
          
          {(result.prediction || result.predictions) && (
            <InfoCard>
              <InfoTitle>🔮 Predicted Candles</InfoTitle>
              <InfoValue>{(result.prediction || result.predictions)?.length || 0} future candlesticks</InfoValue>
            </InfoCard>
          )}
          
          {result.aiStatus && (
            <InfoCard>
              <InfoTitle>🤖 AI Status</InfoTitle>
              <InfoValue style={{ color: result.aiStatus === 'success' ? '#28a745' : '#dc3545' }}>
                {result.aiStatus}
              </InfoValue>
            </InfoCard>
          )}
          
          {result.originalData && (
            <InfoCard>
              <InfoTitle>📈 Original Data</InfoTitle>
              <InfoValue>{result.originalData.length} candlesticks analyzed</InfoValue>
            </InfoCard>
          )}
        </InfoGrid>
        
        {hasImageData && (
          <div style={{ textAlign: 'center' }}>
            <DownloadButton href={result.imageUrl} download onClick={downloadImage}>
              💾 Download Result Image
            </DownloadButton>
          </div>
        )}
        
        {(hasJsonData || (result.stepByStep && result.numericData && result.prediction)) && (
          <DataSection>
            <DataTitle>📈 Raw Data Analysis</DataTitle>
            <p style={{ margin: '10px 0', color: '#666', fontSize: '0.9rem' }}>
              View the numerical OHLC (Open, High, Low, Close) data {hasJsonData ? 'generated for testing' : 'extracted from your image'} 
              and the AI model's predictions.
            </p>
            
            {result.aiMessage && (
              <div style={{ 
                background: '#d1ecf1', 
                padding: '10px', 
                borderRadius: '5px', 
                margin: '10px 0',
                color: '#0c5460',
                fontSize: '0.9rem'
              }}>
                <strong>AI Message:</strong> {result.aiMessage}
              </div>
            )}
            
            <ToggleButton onClick={() => setShowRawData(!showRawData)}>
              {showRawData ? 'Hide' : 'Show'} Raw Data
            </ToggleButton>
            
            {showRawData && (
              <div>
                <div style={{ marginTop: '15px' }}>
                  <DataTitle style={{ fontSize: '1rem' }}>
                    📥 Input Data ({(result.numericData || result.originalData)?.length || 0} candles)
                  </DataTitle>
                  <DataPreview>
                    {formatCandleData(result.numericData || result.originalData || [])}
                  </DataPreview>
                </div>
                
                <div style={{ marginTop: '15px' }}>
                  <DataTitle style={{ fontSize: '1rem' }}>
                    🔮 Predicted Data ({(result.prediction || result.predictions)?.length || 0} candles)
                  </DataTitle>
                  <DataPreview>
                    {formatCandleData(result.prediction || result.predictions || [])}
                  </DataPreview>
                </div>
              </div>
            )}
          </DataSection>
        )}
      </ResultInfo>
      
      <div style={{ marginTop: '20px', padding: '15px', background: '#e8f4f8', borderRadius: '8px' }}>
        <h4 style={{ color: '#0c5460', margin: '0 0 10px 0' }}>
          ℹ️ How to Interpret the Results
        </h4>
        <ul style={{ textAlign: 'left', color: '#0c5460', margin: 0 }}>
          <li><strong>Left side:</strong> Your original candlestick chart (1025×817 pixels)</li>
          <li><strong>Right side:</strong> AI-predicted future candlesticks (342×817 pixels)</li>
          <li><strong>Green candles:</strong> Bullish movement (close price higher than open)</li>
          <li><strong>Red candles:</strong> Bearish movement (close price lower than open)</li>
          <li><strong>Prediction accuracy:</strong> AI model trained on historical patterns</li>
        </ul>
      </div>
    </ResultContainer>
  );
};

export default PredictionResult;