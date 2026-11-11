def test_create_template(client):

    response = client.post(
        "/templates/",
        json={
            "name": "Customer Support",
            "description": "Support prompt",
            "initial_prompt_text": "Hello {name}",
            "author": "Ali",
            "commit_message": "Initial version"
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Customer Support"
    assert len(response.json()["versions"]) == 1


def test_duplicate_template(client):

    payload = {
        "name": "Support",
        "description": "Test",
        "initial_prompt_text": "Hello {name}",
        "author": "Ali",
        "commit_message": "Initial"
    }

    first_response = client.post("/templates/", json=payload)
    second_response = client.post("/templates/", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_list_templates(client):

    client.post(
        "/templates/",
        json={
            "name": "Support",
            "description": "Test",
            "initial_prompt_text": "Hello",
            "author": "Ali",
            "commit_message": "Initial"
        }
    )

    response = client.get("/templates/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_template(client):

    create_response = client.post(
        "/templates/",
        json={
            "name": "Customer Service",
            "description": "Test",
            "initial_prompt_text": "Hello {name}",
            "author": "Ali",
            "commit_message": "Initial"
        }
    )

    template_id = create_response.json()["id"]

    response = client.get(f"/templates/{template_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Customer Service"


def test_get_nonexistent_template(client):

    response = client.get("/templates/9999")

    assert response.status_code == 404
