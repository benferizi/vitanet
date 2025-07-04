import pandas as pd
from flask import Blueprint, jsonify

bp = Blueprint("api", __name__)

@bp.route("/api/data")
def get_data():
    # sample nutrition data
    df = pd.DataFrame([
        {"item": "Apple", "calories": 95, "carbs_g": 25},
        {"item": "Banana", "calories": 105, "carbs_g": 27},
        {"item": "Carrot", "calories": 25, "carbs_g": 6}
    ])
    records = df.to_dict(orient="records")
    return jsonify(records)
