
# MP2 - REST API Data Processing Pipeline

This project is a REST API built using FastAPI for DS3500 Advanced Programming with Data.

The API allows users to upload CSV datasets, store them temporarily in memory, retrieve stored records, and process datasets using the data validation and cleaning functions from MP1. The processing functionality supports validation of required and numeric columns, duplicate removal, missing-value handling, and outlier removal. The application also includes error handling, request logging, unique request IDs, and automated API tests.

## API Endpoints

- GET /health - Check API status and version.
- POST /upload - Upload and store a CSV dataset.
- GET /datasets/{dataset_id} - Retrieve stored dataset records.
- POST /datasets/{dataset_id}/process - Validate and clean a stored dataset.

## Installation

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the API

```bash
python -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs to test the API.

## Testing

Run the automated tests:

```bash
python -m pytest tests -v
```

## Project Structure

- `main.py` - FastAPI application and endpoints
- `src/` - API models, storage, logging, and middleware
- `data_pipeline/` - Reusable data processing functions from MP1
- `fixtures/` - Sample CSV dataset
- `tests/` - Automated API tests
