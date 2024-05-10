import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_example(api_client: AsyncClient):
    json_data = {
        "example_name": "Example Name",
        "example_date": "2024-04-04",
        "example_number": 1,
        "example_status": "A",
        "example_boolean": True,
    }
    response = await api_client.post(
        "/example/",
        json=json_data,
    )
    response_json = response.json()

    assert response.status_code == 200

    # Ensure that all the original data matches
    for key, value in json_data.items():
        assert response_json[key] == value

    # Check additional fields returned by the API
    assert "id" in response_json
    assert "created_at" in response_json
    assert "updated_at" in response_json
