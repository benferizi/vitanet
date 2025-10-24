from flask import Blueprint, jsonify, request

bp = Blueprint("api", __name__)

# Comprehensive nutrition database
NUTRITION_DATABASE = [
    {"item": "Apple", "calories": 95, "carbs_g": 25, "protein_g": 0.3,
     "fat_g": 0.3, "fiber_g": 4.4, "category": "fruit"},
    {"item": "Banana", "calories": 105, "carbs_g": 27, "protein_g": 1.3,
     "fat_g": 0.4, "fiber_g": 3.1, "category": "fruit"},
    {"item": "Carrot", "calories": 25, "carbs_g": 6, "protein_g": 0.5,
     "fat_g": 0.1, "fiber_g": 1.7, "category": "vegetable"},
    {"item": "Broccoli", "calories": 55, "carbs_g": 11, "protein_g": 3.7,
     "fat_g": 0.4, "fiber_g": 5.1, "category": "vegetable"},
    {"item": "Chicken Breast", "calories": 231, "carbs_g": 0, "protein_g": 43.5,
     "fat_g": 5.0, "fiber_g": 0, "category": "protein"},
    {"item": "Salmon", "calories": 208, "carbs_g": 0, "protein_g": 22.1,
     "fat_g": 12.4, "fiber_g": 0, "category": "protein"},
    {"item": "Brown Rice", "calories": 216, "carbs_g": 45, "protein_g": 5.0,
     "fat_g": 1.8, "fiber_g": 3.5, "category": "grain"},
    {"item": "Oats", "calories": 389, "carbs_g": 66, "protein_g": 16.9,
     "fat_g": 6.9, "fiber_g": 10.6, "category": "grain"},
    {"item": "Almonds", "calories": 579, "carbs_g": 22, "protein_g": 21.2,
     "fat_g": 49.9, "fiber_g": 12.5, "category": "nut"},
    {"item": "Greek Yogurt", "calories": 97, "carbs_g": 6, "protein_g": 10.0,
     "fat_g": 5.0, "fiber_g": 0, "category": "dairy"}
]


@bp.route("/api/data")
def get_data():
    """Get all nutrition data"""
    return jsonify(NUTRITION_DATABASE)


@bp.route("/api/foods")
def get_foods():
    """Get all foods with optional category filter"""
    category = request.args.get('category')

    if category:
        filtered_foods = [food for food in NUTRITION_DATABASE
                          if food['category'].lower() == category.lower()]
        return jsonify(filtered_foods)

    return jsonify(NUTRITION_DATABASE)


@bp.route("/api/foods/<food_name>")
def get_food(food_name):
    """Get nutrition data for a specific food"""
    food = next((f for f in NUTRITION_DATABASE
                if f['item'].lower() == food_name.lower()), None)

    if food:
        return jsonify(food)
    else:
        return jsonify({"error": "Food not found"}), 404


@bp.route("/api/categories")
def get_categories():
    """Get all available food categories"""
    categories = list(set(food['category'] for food in NUTRITION_DATABASE))
    return jsonify(sorted(categories))


@bp.route("/api/calculate")
def calculate_nutrition():
    """Calculate total nutrition for a list of foods and quantities"""
    foods = request.args.get('foods', '').split(',')
    quantities = request.args.get('quantities', '').split(',')

    if len(foods) != len(quantities):
        return jsonify({"error": "Foods and quantities must have the same length"}), 400

    total_nutrition = {
        "total_calories": 0,
        "total_carbs_g": 0,
        "total_protein_g": 0,
        "total_fat_g": 0,
        "total_fiber_g": 0,
        "foods": []
    }

    for food_name, qty_str in zip(foods, quantities):
        try:
            quantity = float(qty_str)
        except ValueError:
            return jsonify({"error": f"Invalid quantity for {food_name}: {qty_str}"}), 400

        food = next((f for f in NUTRITION_DATABASE
                    if f['item'].lower() == food_name.lower()), None)
        if not food:
            return jsonify({"error": f"Food not found: {food_name}"}), 404

        # Calculate nutrition for this quantity (assuming quantities are servings)
        food_nutrition = {
            "item": food['item'],
            "quantity": quantity,
            "calories": food['calories'] * quantity,
            "carbs_g": food['carbs_g'] * quantity,
            "protein_g": food['protein_g'] * quantity,
            "fat_g": food['fat_g'] * quantity,
            "fiber_g": food['fiber_g'] * quantity
        }

        total_nutrition["foods"].append(food_nutrition)
        total_nutrition["total_calories"] += food_nutrition["calories"]
        total_nutrition["total_carbs_g"] += food_nutrition["carbs_g"]
        total_nutrition["total_protein_g"] += food_nutrition["protein_g"]
        total_nutrition["total_fat_g"] += food_nutrition["fat_g"]
        total_nutrition["total_fiber_g"] += food_nutrition["fiber_g"]

    # Round totals to 1 decimal place
    for key in total_nutrition:
        if key.startswith("total_") and isinstance(total_nutrition[key], float):
            total_nutrition[key] = round(total_nutrition[key], 1)

    return jsonify(total_nutrition)
