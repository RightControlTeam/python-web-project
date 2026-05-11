from database import db
from datetime import datetime, timezone


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False, index=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)


    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default= lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Review from user {self.user_id} for product {self.product_id}>'
