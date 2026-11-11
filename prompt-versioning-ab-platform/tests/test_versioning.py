
def test_create_new_version(client):

    template = client.post(
        "/templates/",
        json={
            "name": "Support",
            "description": "Test",
            "initial_prompt_text": "Hello {name}",
            "author": "Ali",
            "commit_message": "Version 1"
        }
    )

    template_id = template.json()["id"]

    response = client.post(
        f"/templates/{template_id}/versions/",
        json={
            "prompt_text": "Hello {name}, welcome!",
            "author": "Ali",
            "commit_message": "Version 2"
        }
    )

    assert response.status_code == 201
    assert response.json()["version_number"] == 2


def test_version_history(client):

    template = client.post(
        "/templates/",
        json={
            "name": "History Test",
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
        f"/templates/{template_id}/versions/"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

    assert response.json()[0]["version_number"] == 1
    assert response.json()[1]["version_number"] == 2

    assert response.json()[0]["prompt_text"] == "Hello"

def test_create_multiple_versions_increment_numbers(client):

    template = client.post(
        "/templates/",
        json={
            "name": "Sequential Test",
            "description": "Test version numbering",
            "initial_prompt_text": "Hello",
            "author": "Ali",
            "commit_message": "Version 1"
        }
    )

    template_id = template.json()["id"]

    # Create Version 2
    response_v2 = client.post(
        f"/templates/{template_id}/versions/",
        json={
            "prompt_text": "Hello World",
            "author": "Ali",
            "commit_message": "Version 2"
        }
    )

    # Create Version 3
    response_v3 = client.post(
        f"/templates/{template_id}/versions/",
        json={
            "prompt_text": "Hello World Again",
            "author": "Ali",
            "commit_message": "Version 3"
        }
    )

    assert response_v2.status_code == 201
    assert response_v3.status_code == 201

    assert response_v2.json()["version_number"] == 2
    assert response_v3.json()["version_number"] == 3
    
def test_version_history_missing_template(client):

    response = client.get(
        "/templates/9999/versions/"
    )

    assert response.status_code == 404
