from pymongo import MongoClient
from pymongo.errors import PyMongoError

class Database:
    def __init__(self, db_url, db_name):
        """Initialize the MongoDB client and select the database."""
        try:
            self.client = MongoClient(db_url)  # Establish connection to the MongoDB database
            self.db = self.client[db_name]     # Access the specific database
            self.users = self.db['users']      # Reference to 'users' collection
            print("Database connection established.")
        except PyMongoError as e:
            print(f"Error connecting to database: {e}")
            raise

    def set_api_key(self, user_id, api_key):
        """Set the API key for a given user in the MongoDB collection."""
        try:
            # Update the user's record, or create one if it doesn't exist
            self.users.update_one(
                {'user_id': user_id},  # Find the document with this user_id
                {'$set': {'api_key': api_key}},  # Set the api_key field
                upsert=True  # Insert the document if it doesn't exist
            )
            print(f"API key set for user {user_id}.")
        except PyMongoError as e:
            print(f"Error setting API key: {e}")
            raise

    def get_api_key(self, user_id):
        """Retrieve the API key for a given user from the MongoDB collection."""
        try:
            user_data = self.users.find_one({'user_id': user_id})  # Fetch user data from MongoDB
            if user_data and 'api_key' in user_data:
                return user_data['api_key']
            else:
                return None  # Return None if no API key is found
        except PyMongoError as e:
            print(f"Error getting API key: {e}")
            return None

    def close(self):
        """Close the MongoDB connection."""
        try:
            self.client.close()
            print("Database connection closed.")
        except PyMongoError as e:
            print(f"Error closing database connection: {e}")
            raise
