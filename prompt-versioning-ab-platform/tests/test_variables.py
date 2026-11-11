
from app.services import extract_variables, validate_variables


def test_extract_variables():

    prompt = "Hello {name}, your order is {order_id}"

    result = extract_variables(prompt)

    assert result == ["name", "order_id"]


def test_duplicate_variables():

    prompt = "{name} and {name}"

    result = extract_variables(prompt)

    assert result == ["name"]


def test_valid_variables():

    prompt = "Hello {customer_name}"

    assert validate_variables(prompt) is True


def test_invalid_open_brace():

    prompt = "Hello {customer_name"

    assert validate_variables(prompt) is False


def test_invalid_close_brace():

    prompt = "Hello customer_name}"

    assert validate_variables(prompt) is False


def test_invalid_variable_name():

    prompt = "Hello {123name}"

    assert validate_variables(prompt) is False


def test_api_rejects_invalid_variable(client):

    response = client.post(
        "/templates/",
        json={
            "name": "Invalid Prompt",
            "description": "Test",
            "initial_prompt_text": "Hello {123name}",
            "author": "Ali",
            "commit_message": "Test"
        }
    )

    assert response.status_code == 422


def test_api_rejects_invalid_variable_in_new_version(client):

    template = client.post(
        "/templates/",
        json={
            "name": "Version Variable Test",
            "description": "Test variable validation",
            "initial_prompt_text": "Hello {name}",
            "author": "Ali",
            "commit_message": "Version 1"
        }
    )

    template_id = template.json()["id"]

    response = client.post(
        f"/templates/{template_id}/versions/",
        json={
            "prompt_text": "Hello {user-name}",
            "author": "Ali",
            "commit_message": "Invalid Version"
        }
    )

    assert response.status_code == 422
