import os
import sys
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///db/restaurants.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()


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

    def get_reviews(self):
        return [review for review in self.reviews]

    def get_restaurants(self):
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


if __name__ == '__main__':
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    
    while True:
        print("\n--- Restaurant Management System ---")
        print("1. Add a Review")
        print("2. Delete Reviews")
        print("3. Get All Reviews for a Restaurant")
        print("4. Get Favorite Restaurant for a Customer")
        print("5. Get Fanciest Restaurant")
        print("0. Exit")
        
        choice = input("Enter your choice (0-5): ")
        
        if choice == "1":
            # Add a review
            customer_name = input("Enter customer name: ")
            restaurant_name = input("Enter restaurant name: ")
            rating = int(input("Enter rating (1-5): "))
            
            customer = session.query(Customer).filter_by(full_name=customer_name).first()
            restaurant = session.query(Restaurant).filter_by(name=restaurant_name).first()
            
            if customer and restaurant:
                customer.add_review(restaurant, rating)
                print("Review added successfully!")
            else:
                print("Customer or restaurant not found.")
        
        elif choice == "2":
            # Delete reviews
            customer_name = input("Enter customer name: ")
            restaurant_name = input("Enter restaurant name: ")
            
            customer = session.query(Customer).filter_by(full_name=customer_name).first()
            restaurant = session.query(Restaurant).filter_by(name=restaurant_name).first()
            
            if customer and restaurant:
                customer.delete_reviews(restaurant)
                print("Reviews deleted successfully!")
            else:
                print("Customer or restaurant not found.")
        
        elif choice == "3":
            # Get all reviews for a restaurant
            restaurant_name = input("Enter restaurant name: ")
            
            restaurant = session.query(Restaurant).filter_by(name=restaurant_name).first()
            
            if restaurant:
                reviews = restaurant.all_reviews()
                if reviews:
                    print(f"All Reviews for {restaurant_name}:")
                    for review in reviews:
                        print(review)
                else:
                    print("No reviews found for the restaurant.")
            else:
                print("Restaurant not found.")
        
        elif choice == "4":
            # Get favorite restaurant for a customer
            customer_name = input("Enter customer name: ")
            
            customer = session.query(Customer).filter_by(full_name=customer_name).first()
            
            if customer:
                favorite_restaurant = customer.favorite_restaurant()
                if favorite_restaurant:
                    print(f"{customer_name}'s Favorite Restaurant: {favorite_restaurant.name}")
                else:
                    print("No favorite restaurant found for the customer.")
            else:
                print("Customer not found.")
        
        elif choice == "5":
            # Get fanciest restaurant
            fanciest_restaurant = Restaurant.fanciest()
            if fanciest_restaurant:
                print(f"Fanciest Restaurant: {fanciest_restaurant.name}")
            else:
                print("No restaurants found.")
        
        elif choice == "0":
            # Exit the program
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    print("Thank you for using the Restaurant Management System!")

