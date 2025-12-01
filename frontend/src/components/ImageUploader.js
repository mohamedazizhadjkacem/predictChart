import React from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';

const DropzoneContainer = styled.div`
  border: 3px dashed #4A90E2;
  border-radius: 10px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.isDragActive ? '#f0f8ff' : '#f8f9fa'};
  
  &:hover {
    border-color: #357abd;
    background: #f0f8ff;
  }
`;

const UploadIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 15px;
  color: #4A90E2;
`;

const UploadText = styled.div`
  font-size: 1.1rem;
  margin-bottom: 10px;
  color: #333;
  font-weight: 500;
`;

const UploadSubtext = styled.div`
  font-size: 0.9rem;
  color: #666;
  margin-top: 10px;
`;

const ImagePreviewContainer = styled.div`
  margin-top: 20px;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const ImagePreview = styled.img`
  max-width: 100%;
  height: auto;
  max-height: 400px;
  display: block;
  margin: 0 auto;
`;

const ImageInfo = styled.div`
  background: #f8f9fa;
  padding: 15px;
  text-align: left;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 0.9rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const InfoLabel = styled.span`
  font-weight: 500;
  color: #555;
`;

const InfoValue = styled.span`
  color: #333;
`;

const ImageUploader = ({ onFileUpload, uploadedImageUrl, isProcessing }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onFileUpload,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple: false,
    disabled: isProcessing
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div>
      {!uploadedImageUrl ? (
        <DropzoneContainer {...getRootProps()} isDragActive={isDragActive}>
          <input {...getInputProps()} />
          <UploadIcon>📊</UploadIcon>
          <UploadText>
            {isDragActive 
              ? "Drop the candlestick chart here..." 
              : "Click or drag to upload a candlestick chart image"
            }
          </UploadText>
          <UploadSubtext>
            Supports PNG, JPG, GIF, WebP • Max size: 10MB
            <br />
            Recommended: 1025×817 resolution for best results
          </UploadSubtext>
        </DropzoneContainer>
      ) : (
        <div>
          <ImagePreviewContainer>
            <ImagePreview src={uploadedImageUrl} alt="Uploaded candlestick chart" />
          </ImagePreviewContainer>
          
          {!isProcessing && (
            <div style={{ textAlign: 'center', marginTop: '15px' }}>
              <DropzoneContainer {...getRootProps()} isDragActive={isDragActive}>
                <input {...getInputProps()} />
                <UploadIcon style={{ fontSize: '2rem', margin: '10px 0' }}>🔄</UploadIcon>
                <UploadText style={{ fontSize: '1rem' }}>
                  Click to upload a different image
                </UploadText>
              </DropzoneContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;