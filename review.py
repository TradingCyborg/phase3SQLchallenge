from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Create a SQLAlchemy engine and session
engine = create_engine("sqlite:///restaurant_reviews.db")
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Define the models for Customer, Restaurant, and Review
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        reviews = [review for review in self.reviews]
        if reviews:
            return max(reviews, key=lambda x: x.rating).restaurant
        else:
            return None

    def add_review(self, restaurant, rating):
        new_review = Review(customer=self, restaurant=restaurant, rating=rating)
        session.add(new_review)
        session.commit()

    def delete_reviews(self, restaurant):
        for review in self.reviews:
            if review.restaurant == restaurant:
                session.delete(review)
        session.commit()

    # Establishing a one-to-many relationship between Customer and Review
    reviews = relationship("Review", back_populates="customer")

    def restaurants(self):
        return [review.restaurant for review in self.reviews]

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

    # Establishing a one-to-many relationship between Restaurant and Review
    reviews = relationship("Review", back_populates="restaurant")

    def customers(self):
        return [review.customer for review in self.reviews]

    @classmethod
    def fanciest(cls):
        return session.query(Restaurant).order_by(Restaurant.price.desc()).first()

    def all_reviews(self):
        review_strings = []
        for review in self.reviews:
            review_strings.append(review.full_review())
        return review_strings

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    rating = Column(Integer)

    # Establishing many-to-one relationships with Customer and Restaurant
    customer = relationship("Customer", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")

    def full_review(self):
        return f"Rating: {self.rating}, Review by: {self.customer.full_name()}, Restaurant: {self.restaurant.name}"

Base.metadata.create_all(engine)

# Example usage:
if __name__ == "__main__":
    # Create some sample data
    customer1 = Customer(first_name="james", last_name="bond")
    customer2 = Customer(first_name="john", last_name="wick")
    customer3 = Customer(first_name="keanu", last_name="reeves")
    restaurant1 = Restaurant(name="Risen", price=4.5)
    restaurant2 = Restaurant(name="lily's place", price=2.0)
    restaurant3 = Restaurant(name="pizza hut", price=3.8)
    
    session.add_all([customer1, customer2, customer3, restaurant1, restaurant2, restaurant3])
    session.commit()

    # Add reviews
    customer1.add_review(restaurant1, 5)
    customer1.add_review(restaurant2, 4)
    customer2.add_review(restaurant1, 4)
    customer3.add_review(restaurant3, 5)
    
    
    # Print restaurant info
    print(f"Fanciest Restaurant: {Restaurant.fanciest().name}")
    
    # Print all reviews for a restaurant
    for review in restaurant1.all_reviews():
        print(review)