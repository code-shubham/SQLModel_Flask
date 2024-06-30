from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint, abort
from sqlmodel import Field, Session, SQLModel, create_engine, select
from marshmallow import Schema, fields

# Define the SQLModel
class User(SQLModel, table=True):
    id: int = Field( primary_key=True)
    name: str
    email: str

# Create the SQLite engine
engine = create_engine("sqlite:///database.db")

# Create the tables
SQLModel.metadata.create_all(engine)

# Initialize Flask app
app = Flask(__name__)

# Configure API documentation
app.config["API_TITLE"] = "User API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_JSON_PATH"] = "api-spec.json"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

blp = Blueprint("users", "users", url_prefix="/users", description="Operations on users")

# Schemas for request/response serialization
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)

@blp.route("/")
class Users(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        """List all users"""
        with Session(engine) as session:
            users = session.exec(select(User)).all()
        return users

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user"""
        user = User(**user_data)
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

@blp.route("/<int:user_id>")
class UserById(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get a user by ID"""
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                abort(404, message="User not found")
        return user

api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(debug=True)