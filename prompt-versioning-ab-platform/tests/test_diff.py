
from app.services import compute_text_diff


def test_diff_added_text():

    result = compute_text_diff(
        "Hello\n",
        "Hello World\n"
    )

    assert "-Hello" in result
    assert "+Hello World" in result


def test_diff_removed_text():

    result = compute_text_diff(
        "Hello World\n",
        "Hello\n"
    )

    assert "-Hello World" in result
    assert "+Hello" in result


def test_identical_text():

    result = compute_text_diff(
        "Hello\n",
        "Hello\n"
    )

    assert result == ""


def test_api_diff(client):

    template = client.post(
        "/templates/",
        json={
            "name": "Diff Test",
            "description": "Test",
            "initial_prompt_text": "Hello",
            "author": "Ali",
            "commit_message": "V1"
        }
    )

    template_id = template.json()["id"]

    client.post(
        f"/templates/{template_id}/versions/",
        json={
            "prompt_text": "Hello World",
            "author": "Ali",
            "commit_message": "V2"
        }
    )

    response = client.get(
        f"/templates/{template_id}/diff?v1=1&v2=2"
    )

    assert response.status_code == 200
    assert response.json()["version_a"] == 1
    assert response.json()["version_b"] == 2
    assert "+Hello World" in response.json()["diff_text"]


def test_api_diff_missing_version(client):

    template = client.post(
        "/templates/",
        json={
            "name": "Missing Version Test",
            "description": "Test missing version",
            "initial_prompt_text": "Hello",
            "author": "Ali",
            "commit_message": "V1"
        }
    )

    template_id = template.json()["id"]

    response = client.get(
        f"/templates/{template_id}/diff?v1=1&v2=999"
    )

    assert response.status_code == 404
