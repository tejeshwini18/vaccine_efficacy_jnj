# Vaccine Efficacy Analysis Application

This application processes medical records to analyze vaccine efficacy and adverse effects. It extracts data from PDF files, performs OCR (Optical Character Recognition), and generates analysis reports.

## Features

- PDF file processing with OCR capabilities
- Extraction of medical data including:
  - Patient demographics
  - Vital signs (BP, Height, Weight, Pulse, SpO2)
  - Symptoms and diagnoses
  - Medication information
- Adverse effects analysis
- Data export to CSV format
- Docker and Kubernetes deployment support

## Prerequisites

- Python 3.9 or higher
- Tesseract OCR
- Docker Desktop (for containerization)
- Kubernetes cluster (for deployment)

## System Requirements

- Windows 10 Pro/Enterprise/Education (64-bit)
- At least 4GB RAM
- Virtualization enabled in BIOS
- Docker Desktop with WSL 2 support

## Installation

### 1. Local Development Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - Add to system PATH

### 2. Docker Setup

1. Install Docker Desktop:
   - Download from: https://www.docker.com/products/docker-desktop
   - Enable WSL 2 during installation
   - Restart your computer

2. Build Docker image:
   ```bash
   docker build -t vaccine-efficacy-app:latest .
   ```

### 3. Kubernetes Deployment

1. Apply Kubernetes configurations:
   ```bash
   kubectl apply -f deployment.yaml
   ```

2. Verify deployment:
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get pvc
   ```

## Project Structure

```
vaccine_efficacy_jnj/
├── new_backend/
│   └── zipped_extraction.py    # Main application code
├── Upload_Folder/             # Directory for uploaded files
│   └── debug_images/         # Debug images from OCR processing
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
├── deployment.yaml           # Kubernetes configuration
└── README.md                # This file
```

## Usage

1. Place PDF files in the `Upload_Folder` directory
2. Run the application:
   ```bash
   python new_backend/zipped_extraction.py
   ```
3. Check the `Upload_Folder` for generated CSV files:
   - `extracted_data.csv`: All extracted data
   - `AdverseEffect.csv`: Records with adverse effects
   - `Filtered_Data.csv`: Filtered dataset

## Data Output

The application generates three CSV files:
1. `extracted_data.csv`: Complete extracted data from all PDFs
2. `AdverseEffect.csv`: Records containing vaccine-related adverse effects
3. `Filtered_Data.csv`: Filtered dataset based on specific criteria

## Docker Commands

- Build image:
  ```bash
  docker build -t vaccine-efficacy-app:latest .
  ```

- Run container:
  ```bash
  docker run -v $(pwd)/Upload_Folder:/app/Upload_Folder vaccine-efficacy-app:latest
  ```

## Kubernetes Commands

- Deploy application:
  ```bash
  kubectl apply -f deployment.yaml
  ```

- Check deployment status:
  ```bash
  kubectl get pods
  kubectl get services
  kubectl get pvc
  ```

- View logs:
  ```bash
  kubectl logs -f deployment/vaccine-efficacy-app
  ```

## Troubleshooting

1. Docker not recognized:
   - Ensure Docker Desktop is installed and running
   - Check if Docker service is running in Services
   - Verify system PATH includes Docker

2. Tesseract OCR issues:
   - Verify Tesseract installation path
   - Check if `tesseract.exe` is in system PATH
   - Ensure language data files are installed

3. Kubernetes deployment issues:
   - Check pod status: `kubectl describe pod <pod-name>`
   - Verify persistent volume claims: `kubectl get pvc`
   - Check service status: `kubectl get services`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.