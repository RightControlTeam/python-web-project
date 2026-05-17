from flask import request, jsonify
from app import app
from jwt_decoding import decode_jwt
from .review_service import ReviewService
from schemas import ReviewCreateRequest, ReviewUpdateRequest
from pydantic import ValidationError
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "AUTH_REQUIRED", "detail": "The Authorization header is missing"}), 401

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "INVALID_FORMAT", "detail": "Incorrect header format"}), 401

        user_data = decode_jwt(token)
        if not user_data:
            return jsonify({"error": "INVALID_TOKEN", "detail": "Token is invalid "}), 401

        request.user = user_data
        return f(*args, **kwargs)
    return decorated

@app.route('/reviews', methods=['POST'])
@token_required
async def create_review():
    try:
        data = ReviewCreateRequest(**request.json)

        new_review = await ReviewService.create(data, user_id=int(request.user['sub']))

        if not new_review:
            return jsonify({"error": "NOT_FOUND", "detail": "Product does not exist "}), 404

        return jsonify({"id": new_review.id, "status": new_review.status}), 201
    except ValidationError as e:
        return jsonify({"error": "VALIDATION_ERROR", "detail": e.errors()}), 400

@app.route('/reviews/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    reviews = ReviewService.find_by_product_id(product_id)
    return jsonify([{
        "id": r.id,
        "user_id": r.user_id,
        "text": r.text,
        "rating": r.rating,
        "created_at": r.created_at.isoformat()
    } for r in reviews]), 200

@app.route('/reviews/<int:review_id>', methods=['PUT'])
@token_required
def update_review(review_id):
    try:
        data = ReviewUpdateRequest(**request.json)
        updated = ReviewService.update_review(
            data,
            review_id=review_id,
            user_id=int(request.user['sub'])
        )
        if not updated:
            return jsonify({"error": "FORBIDDEN", "detail": "Access denied"}), 403
        return jsonify({"message": "Updated successfully"}), 200
    except ValidationError as e:
        return jsonify({"error": "VALIDATION_ERROR", "detail": e.errors()}), 400

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review(review_id):
    is_admin = request.user.get('is_admin', False)

    success = ReviewService.delete_by_id(
        review_id=review_id,
        user_id=int(request.user['sub']),
        is_admin=is_admin
    )

    if not success:
        return jsonify({"error": "NOT_ALLOWED", "detail": "Review not found or no permission"}), 403
    return jsonify({"message": "Review deleted"}), 200