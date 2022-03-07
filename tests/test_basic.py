from api.models import db, User


# client passed from client - look into pytest for more info about fixtures
# test client api: http://flask.pocoo.org/docs/1.0/api/#test-client
def test_index(client):
    rs = client.get("/")
    assert rs.status_code == 200


def test_get_person(client):
    rs = client.get("/users")

    assert rs.status_code == 200
    ret_dict = rs.json  # gives you a dictionary
    assert ret_dict["success"] == True
    assert ret_dict["result"]["users"] == []

    # create User and test whether it returns a person
    temp_user = User(name="Tim", dob="02/01/1998", zip="94085")
    db.session.add(temp_user)
    db.session.commit()

    rs = client.get("/users")
    ret_dict = rs.json
    assert len(ret_dict["result"]["users"]) == 1
    assert ret_dict["result"]["users"][0]["name"] == "Tim"
