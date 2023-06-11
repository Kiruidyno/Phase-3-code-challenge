import os
import sys
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

sys.path.append(os.getcwd())

Base = declarative_base()
engine = create_engine('sqlite:///db/restaurants.db', echo=True)


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer)
    comment = Column(Text)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer = relationship("Customer", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.rating} stars."


class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True)
    name = Column(String())
    price = Column(Integer)
    reviews = relationship('Review', back_populates='restaurant')

    @classmethod
    def fanciest(cls):
        return session.query(cls).order_by(cls.price.desc()).first()

    def all_reviews(self):
        review_strings = []
        for review in self.reviews:
            review_strings.append(review.full_review())
        return review_strings

    def __repr__(self):
        return f'Restaurant: {self.name}'


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String())
    last_name = Column(String())
    reviews = relationship('Review', back_populates='customer')

    def reviews(self):
        return [review for review in self.reviews]

    def restaurants(self):
        return [review.restaurant for review in self.reviews]

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def favorite_restaurant(self):
        max_rating = 0
        favorite_restaurant = None
        for review in self.reviews:
            if review.rating > max_rating:
                max_rating = review.rating
                favorite_restaurant = review.restaurant
        return favorite_restaurant

    def add_review(self, restaurant, rating):
        review = Review(customer=self, restaurant=restaurant, rating=rating)
        session.add(review)
        session.commit()

    def delete_reviews(self, restaurant):
        session.query(Review).filter_by(customer=self, restaurant=restaurant).delete()
        session.commit()

    def __repr__(self):
        return f'Customer: {self.first_name} {self.last_name}'
