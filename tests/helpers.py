from managers.auth_manager import AuthManager


def assert_count_equal(count, model):
    assert len(model.query.all()) == count


def generate_token(user):
    token = AuthManager.encode_token(user)
    return token


def mock_uuid():
    return "12345678-1234-5678-1234-567812345678"