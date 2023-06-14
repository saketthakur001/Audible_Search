# ```Pyhton
# Importing Flask and other modules
from flask import Flask, render_template, request
import pandas as pd
import sqlite3

# Creating a Flask app
app = Flask(__name__)

database_location = r"C:\Users\saket\Documents\GitHub\Pyhton\web scraping\audible.db"
database_location = r"audible.db"
class AudibleDB:

    # Define a method to create the database and table
    def create_db(self):

        # Connect to the database file or create it if it does not exist
        self.conn = sqlite3.connect(database_location)

        # Create a cursor object to execute SQL commands
        self.cur = self.conn.cursor()

        # Create a table called audiobooks with the following columns and data types
        # Create a table called audiobooks with the following columns and data types
        self.cur.execute("""CREATE TABLE IF NOT EXISTS audiobooks (
                        title TEXT,
                        subtitle TEXT,
                        author TEXT,
                        narrator TEXT,
                        series TEXT,
                        length INTEGER,
                        release_date TEXT,
                        language TEXT,
                        summary TEXT,
                        image TEXT,
                        link TEXT PRIMARY KEY,
                        ratings REAL,
                        votes INTEGER
                    )
                    """)

        # Commit the changes to the database
        self.conn.commit()

    # Define a method to insert data into the table
    def insert_data(self, data):

        # Loop through each item in the data list
        for item in data:
            # print(item)
            # Extract the values from the dictionary
            title = item["title"]
            subtitle = item["subtitle"]
            author = item["author"]
            narrator = item["narrator"]
            series = item["series"]
            length = item["length"]
            release_date = item["release_date"]
            language = item["language"]
            summary = item["summary"]
            image = item["image"]
            link = item["link"]
            ratings = item["ratings"]
            votes = item["votes"]
            # votes = item.get("votes", 0) # This will return 0 if "votes" is not in item
            # Insert the values into the table using placeholders and a tuple if it already doesn't exist
            self.cur.execute("""INSERT OR IGNORE INTO audiobooks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                                ON CONFLICT(link) DO NOTHING;
                                """,
                             (title, subtitle, author, narrator, series, length, release_date, language, summary, image, link, ratings, votes))
                             # print if data is inserted
            # print(title)
            # # print the new inserted titles
            if self.cur.rowcount != 0:
                print(title)

        # Commit the changes to the database
        self.conn.commit()

    def read_data(self, **kwargs):
        # Define the base query
        query = "SELECT * FROM audiobooks WHERE 1=1"

        # Define the parameters for the query
        params = []

        # Add the filters to the query and parameters
        if kwargs.get("author"):
            query += " AND author=?"
            params.append(kwargs["author"])
        if kwargs.get("narrator"):
            query += " AND narrator=?"
            params.append(kwargs["narrator"])
        if kwargs.get("series"):
            query += " AND series=?"
            params.append(kwargs["series"])
        if kwargs.get("language"):
            query += " AND language=?"
            params.append(kwargs["language"])
        if kwargs.get("min_length"):
            query += " AND length>=?"
            params.append(kwargs["min_length"])
        if kwargs.get("min_rating"):
            query += " AND ratings>=?"
            params.append(kwargs["min_rating"])
        if kwargs.get("min_votes"):
            query += " AND votes>=?"
            params.append(kwargs["min_votes"])
        if kwargs.get("search"):
            search_terms = kwargs["search"].split()
            for term in search_terms:
                query += " AND (title LIKE ? OR subtitle LIKE ? OR author LIKE ? OR narrator LIKE ? OR summary LIKE ?)"
                params.extend(["%{}%".format(term)] * 5)

        # Add the sorting to the query
        sort_by = kwargs.get("sort_by", "title")
        sort_order = kwargs.get("sort_order", "ASC")
        query += " ORDER BY {} {}".format(sort_by, sort_order)

        # Execute the query and get the results
        self.cur.execute(query, params)
        results = self.cur.fetchall()

        # Return the results
        return results

    # Define a method to close the connection to the database
    def close_db(self):
        self.conn.close()

db = AudibleDB()
db.create_db()
lis = db.read_data()
# print(lis)

df = pd.DataFrame(lis, columns=['title', 'subtitle', 'author', 'narrator', 'series', 'length', 'release_date', 'language', 'summary', 'image_url', 'link', 'rating', 'votes'])

# Extracting the year from the release_date column
df['year'] = df['release_date'].str.split('.').str[0]

def get_input():
    print('enter a test score below')
    user_in = input()
    if not user_in or not user_in.isdigit(): # check if input is empty or non-numeric
        print('error, you must enter a numeric value.')
        return get_input()
    elif len(user_in) > 2: # check if input is too long
        print('error, you can only enter a 2 digit number.')
        return get_input()
    else:
        return user_in
# Creating a route for the homepage
@app.route('/')
def home():
    # Getting the query parameters from the request
    search = request.args.get('search')
    sort_by = request.args.get('sort_by')
    author = request.args.get('author')
    narrator = request.args.get('narrator')
    series = request.args.get('series')
    language = request.args.get('language')
    min_length = request.args.get('min_length', 0) # default value is 0
    min_rating = request.args.get('min_rating', 0)
    # min_votes = request.args.get('min_votes')
    min_votes = request.args.get('min_votes', 0)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=100, type=int)

    # Validating the query parameters
    try:
        min_length = int(min_length)
        min_rating = float(min_rating)
        min_votes = int(min_votes)
    except ValueError:
        # Handle invalid values here
        # For example, return an error message or use default values
        return "Invalid query parameters"


    # Filtering and sorting the dataframe based on the query parameters
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search) | 
                                  filtered_df['author'].str.contains(search) |
                                  filtered_df['narrator'].str.contains(search) |
                                  filtered_df['series'].str.contains(search) |
                                  filtered_df['language'].str.contains(search)]
    if sort_by:
        filtered_df = filtered_df.sort_values(by=sort_by)
    if author:
        filtered_df = filtered_df[filtered_df['author'] == author]
    if narrator:
        filtered_df = filtered_df[filtered_df['narrator'] == narrator]
    if series:
        filtered_df = filtered_df[filtered_df['series'] == series]
    if language:
        filtered_df = filtered_df[filtered_df['language'] == language]
    
    # Filtering the dataframe by the length column based on the min_length parameter
    filtered_df = filtered_df[filtered_df['length'] >= int(min_length)]

    if min_rating:
        filtered_df = filtered_df[filtered_df['rating'] >= float(min_rating)]
    if min_votes:
        filtered_df = filtered_df[filtered_df['votes'] >= int(min_votes)]
        

    # Paginating the dataframe based on the page and per_page parameters
    paginated_df = filtered_df.iloc[(page-1)*per_page:page*per_page]

    # Converting the dataframe into a list of dictionaries
    data = paginated_df.to_dict(orient='records')

    # Rendering the template with the data and query parameters
    # Passing the sort_by parameter as well
    return render_template('index.html', data=data, df=df, search=search, author=author, narrator=narrator, series=series, language=language, min_length=min_length, min_rating=min_rating, min_votes=min_votes, page=page, per_page=per_page, sort_by=sort_by)




# Running the app
if __name__ == '__main__':
    app.run(debug=True)


# ```
