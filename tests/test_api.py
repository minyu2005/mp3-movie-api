
def test_upload_csv(client, sample_csv_bytes):
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample_data.csv",
                sample_csv_bytes,
                "text/csv"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["rows"] == 6
    assert data["columns"] == 2
    assert isinstance(data["id"], int)
    assert data["id"] > 0


def test_process_and_retrieve(
    client, uploaded_dataset_id, processing_body
):
    response = client.post(
        f"/datasets/{uploaded_dataset_id}/process",
        json=processing_body
    )

    assert response.status_code == 200

    report = response.json()
    assert report["id"] == uploaded_dataset_id
    assert report["validation_rows_removed"] == 1

    cleaning_report = report["cleaning_report"]
    assert cleaning_report["rows_before"] == 5
    assert cleaning_report["rows_after"] == 3
    assert cleaning_report["rows_removed"] == 2
    assert cleaning_report["columns_before"] == 2
    assert cleaning_report["columns_after"] == 2
    assert cleaning_report["columns_removed"] == 0

    retrieve_response = client.get(
        f"/datasets/{uploaded_dataset_id}"
    )

    assert retrieve_response.status_code == 200

    retrieved = retrieve_response.json()
    assert retrieved["total_rows"] == 3

    records = retrieved["data"]

    actual = {
        int(row["student_id"]): float(row["score"])
        for row in records
    }

    assert actual == {
        1: 80.0,
        2: 90.0,
        5: 85.0
    }


def test_retrieve_missing_dataset(client):
    response = client.get("/datasets/999")
    assert response.status_code == 404
