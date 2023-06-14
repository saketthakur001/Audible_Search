import re
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import datetime
import time

def get_authors(text, string=True):
  try:
    return text.split('by: ')[1]#.split(', ')
    
  except:
    # if string: return text.join(', ')
    return None #[None]

# Send a GET request to the URL of this page

def generate_link(page=1, main_category="Science Fiction & Fantasy", genre="Science Fiction", author_author="", keywords="", narrator="", publisher="", sort="", title="", pageSize=50, language="English"):
  # sort = "Popular", "Relevance", "Newest Arrivals", "Customer Rating", "Price - Low to High", "Price - High to Low", "Featured", "Avg. Customer Review"
  # main_category = "Science Fiction & Fantasy", "Romance", "Mystery, Thriller & Suspense", etc.
  # genre = "Science Fiction", "Fantasy", "Sci-Fi & Fantasy Anthologies", etc.
  # language = "English", "Spanish", "French", etc.

  base_url = "https://www.audible.com/search?"
  # A dictionary that maps main category names to audible_programs values
  main_category_dict = {
    "Science Fiction & Fantasy": "20956260011",
    "Romance": "2226655011",
    "Mystery, Thriller & Suspense": "18580609011",
    # Add more main categories as needed
  }
  # A dictionary that maps genre names to node values
  genre_dict = {
    "Science Fiction": "18580606011",
    "Fantasy": "18580607011",
    "Sci-Fi & Fantasy Anthologies": "18580608011",
    # Add more genres as needed
  }
  # A dictionary that maps language names to feature_six_browse-bin values
  language_dict = {
    "English": "18685580011",
    "Spanish": "18685581011",
    "French": "18685582011",
    # Add more languages as needed
  }
  params = {
    "audible_programs": main_category_dict.get(main_category, ""), # Get the value from the dictionary or use an empty string if not found
    "author_author": author_author,
    "keywords": keywords,
    "narrator": narrator,
    "pageSize": pageSize,
    "publisher": publisher,
    "sort": sort,
    "title": title,
    "node": genre_dict.get(genre, ""), # Get the value from the dictionary or use an empty string if not found
    "feature_six_browse-bin": language_dict.get(language, ""), # Get the value from the dictionary or use an empty string if not found
    "ref": f"a_search_l1_audible_programs_{language_dict.get(language, '0')[-2:]}", # Use the last two digits of the feature_six_browse-bin value for the ref parameter
    "pf_rd_p": "daf0f1c8-2865-4989-87fb-15115ba5a6d2",
    "pf_rd_r": "3CSM3Q3AG46QRQ0TVK0F",
    "pageLoadId": "dELu6hUurPGV8fAu",
    "creativeId": "9648f6bf-4f29-4fb4-9489-33163c0bb63e"
  }
  if page > 1:
    params["page"] = page
  query = "&".join([f"{key}={value}" for key, value in params.items()])
  return base_url + query



# convert string to date object
def string_to_date(text):
    '''
    Convert string to date object
    datetime.date
        year in float
        ex: 2013.2993150684931
    '''
    if text == None:
        return None
    elif 'Release date: ' in text:
        month, day, year = text.split('Release date: ')[1].split('-')
        year = "20"+year
        # month, day, year = map(int, text.split('-'))
        date =  datetime.date(int(year), int(month), int(day))
        return date.year+ date.month/12 + date.day/365
    # check if text is float or int
    elif text.isnumeric():
        return text


# convert string to date object
def extract_rating(string):
    if string == "Not rated yet" or string == None:
        return None, None
    string = string.split(' out of 5 stars ')
    rating = float(string[0])
    votes = int(string[1].split(' rating')[0].replace(',',''))
    return rating, votes


# hour and min to min
def hour_min_to_min(tim):
    if tim == None:
        return None
    elif 'min' not in tim:
        return int(tim.split('Length: ')[1].split(' hr')[0])*60
    elif 'hr' not in tim:
        return int(tim.split('Length: ')[1].split(' min')[0])
    else:
        hr = tim.split('Length: ')[1].split(' hr')[0]
        minute = tim.split("and ")[1].split(' min')[0]
    return int(hr)*60 + int(minute)

def scrape_all_details(page):
# Send a GET request to the page and parse the HTML content
  response = requests.get(page)
  soup = BeautifulSoup(response.content, "html.parser")

  # Find all the elements that contain the product details
  products = soup.find_all("div", class_="bc-col-responsive bc-col-6")

  # Create an empty list to store the details
  details_list = []

  img_tags = soup.find_all("img")
  # list of image
  urls = []
  # Loop through the img tags and get the src attribute of each one
  for i, img_tag in enumerate(img_tags):
    try:
      src = img_tag["src"]
      # print(src) # Print the image URL
      urls.append(src)

    except:
      src = None
      urls.append(src)
      # print(src) # Print the image URL
  cover_image = []
  for image_link in urls:
    if "https://m.media-amazon.com/images/I" in image_link or ".jpg" in image_link:
      # print(image_link)
      cover_image.append(image_link)
  if len(cover_image) % 10 != 0:
    print(f"found {len(cover_image)} images found must be the last page or and error occured")
    # return None
  else:
    print(f"Success: {len(cover_image)} images found")

# Loop through each product element and extract the details
  for product in products:
    # Try to find the title element and handle the exception if not found
    try:
      title = product.find("h3", class_="bc-heading").text.strip()
    except AttributeError:
      title = None
      continue
    # Try to find the subtitle element and handle the exception if not found
    try:
      # get the li element with class subtitle
      subtitle = product.find("li", class_="bc-list-item subtitle").text.strip()
    except AttributeError:
      subtitle = None

    # Try to find the author element and handle the exception if not found
    try:
      author = product.find("li", class_="authorLabel").text.strip()
    except AttributeError:
      author = None
    # Try to find the narrator element and handle the exception if not found
    try:
      narrator = product.find("li", class_="narratorLabel").text.strip()
    except AttributeError:
      narrator = None
    try:
      series = product.find("li", class_="seriesLabel").text.strip()
    except AttributeError:
      series = None
    try:
      length = product.find("li", class_="runtimeLabel").text.strip()
    except AttributeError:
      length = None
    try:
      release_date = product.find("li", class_="releaseDateLabel").text.strip() 
    except AttributeError:
      release_date = None
    try:
      language = product.find("li", class_="languageLabel").text.strip()
    except AttributeError:
      language = None

    try:
      ratings = product.find("li", class_="ratingsLabel").text.strip()
    except AttributeError:
      ratings = None

    # Try to find the summary element and handle the exception if not found
    try:
      summary = product.find("p", class_="bc-text").text.strip()
    except AttributeError:
      summary = None

    image = None

    # Try to find the link element and handle the exception if not found
    try:
      link = product.find("a", class_="bc-link bc-color-link").get("href")
    except AttributeError:
      link = None

    # Create a dictionary with the product details
    details_dict = {
      "title"        : title,
      "subtitle"     : subtitle,
      "author"       : author,
      "narrator"     : narrator,
      "series"       : series,
      "length"       : length,
      "release_date" : release_date,
      "language"     : language,
      "ratings"      : ratings,
      "vote"         : None,
      "summary"      : summary,
      "image"        : image, # Add this line
      "link"         : link # Add this line
    }
    # Format the values using strip and replace methods
    for key, value in details_dict.items():
      # Remove leading and trailing whitespaces
      if value is None: continue
      value = value.strip()
      # Replace multiple whitespaces with a single space using re.sub
      value = re.sub("\s+", " ", value)
      # Update the dictionary with the formatted value
      details_dict[key] = value
      
    # Append the dictionary to the list
    details_list.append(details_dict)
    try:
      details_dict['series'] = details_dict['series'].split('Series: ')[1]
    except:
      details_dict['series'] = None
    try:
      details_dict['author'] = details_dict['author'].split('By: ')[1]
    except:
      details_dict['author'] = None
    # narrator
    try:
      details_dict['narrator'] = details_dict['narrator'].split("Narrated by: ")[1]
    except:
      details_dict['narrator'] = None
    # modify length
    details_dict['length'] = hour_min_to_min(details_dict['length'])
    # language
    try:
      details_dict['language'] = details_dict['language'].split('Language: ')[1]
    except:
      details_dict['language'] = None
    # add vote
    details_dict['votes'] = extract_rating(details_dict['ratings'])[1]
    # modify ratings
    details_dict['ratings'] = extract_rating(details_dict['ratings'])[0]
    # modify release date
    details_dict['release_date'] = string_to_date(details_dict['release_date'])

  # add cover image to the dictionary in the list
  for i in range(len(details_list)):
    details_list[i]["image"] = cover_image[i]

  # Return the list with all the details
  return details_list
# Define a class for the database operations
class AudibleDB:

    # Define a method to create the database and table
    def create_db(self):

        # Connect to the database file or create it if it does not exist
        self.conn = sqlite3.connect("audible.db")

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
# data = scrape_all_details(generate_link())
# request = requests.get(generate_link())
# soup = BeautifulSoup(request.text, "html.parser")

# data = scrape_all_details(generate_link())

genre_dict = {
  "Science Fiction": "18580606011",
  "Fantasy": "18580607011",
  "Sci-Fi & Fantasy Anthologies": "18580608011",
  "Arts & Entertainment": "18571910011",
  "Music": "18571942011",
  "Art": "18571913011",
  "Entertainment & Performing Arts": "18571923011",
  "Computers & Technology": "18573211011",
  "Education & Learning": "18573267011",
  "Education": "18573268011",
  "Erotica": "18573351011",
  "Comedy & Humor": "24427740011",
  "Literature & Fiction": "18574426011",
  "Genre Fiction": "18574456011",
  "Psychological": "18574475011",
  "Coming of Age": "18574461011",
  "Biographies & Memoirs": "18571951011",
  "True Crime": "18572017011",
  "Adventurers, Explorers & Survival": "18571952011",
  "Professionals & Academics": "18572005011",
  "Teen & Young Adult": "18580715011",
  "Romance": "18581004011",
  "Money & Finance": "18574547011",
  "Mystery, Thriller & Suspense": "18574597011",
  "Relationships, Parenting & Personal Development": "18574784011"
}

def Romance(page, num=1):
  if num == 1: 
    genre = "Romance"
    return  f"https://www.audible.com/search?audible_programs=20956260011&author_author=&feature_six_browse-bin=18685580011&keywords=&narrator=&node=18580518011&pageSize=50&publisher=&sort=review-rank&title=&page={page}&ref=a_search_c4_pageNum_1&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=3GZFCRJHPG11J59H39ZN&pageLoadId=M2BR61OaYlu76sSQ&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a"
  # if num == 2:
  #   genre = "Romance Full-cast"
  #   return https://www.audible.com/search?audible_programs=20956260011&crid=70065a2f6d0546e2b9cc499cea9af17f&i=na-audible-us&k=full-cast&keywords=full-cast&node=18580518011&pageSize=50&ref-override=a_search_t1_header_search&sort=review-rank&sprefix=full-cast%2Cna-audible-us%2C960&url=search-alias%3Dna-audible-us&ref=a_search_l1_catRefs_13&pf_rd_p=daf0f1c8-2865-4989-87fb-15115ba5a6d2&pf_rd_r=12NJ2M465JDCAWBN4MP2&pageLoadId=M0VkzU814kP9Ue6q&creativeId=9648f6bf-4f29-4fb4-9489-33163c0bb63e"

# def full_cast_paid_inclueded(page, num=1):
#   if num == 1:
#     return f"https://www.audible.com/search?crid=70065a2f6d0546e2b9cc499cea9af17f&i=na-audible-us&k=full-cast&keywords=full-cast&pageSize=50&ref-override=a_search_t1_header_search&sprefix=full-cast%2Cna-audible-us%2C960&url=search-alias%3Dna-audible-us&page={page}&ref=a_search_c4_pageNum_1&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=BW6P896DE9C8RQ7FAMX1&pageLoadId=k3CpdC9xU4rOObAb&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a"



# print(generate_link())
if __name__ == "__main__":
    start_page = 2
    end_page = 10
    # Create an instance of the class
    db = AudibleDB()
    # Call the create_db method to create the database and table
    db.create_db()
    while start_page <= end_page:
        sort ="review-rank" "Popular", "Relevance", "Newest Arrivals", "Customer Rating", "Price - Low to High", "Price - High to Low", "Featured", "Avg. Customer Review"
        link = generate_link(page=start_page, narrator="", sort="review-rank", genre="Romance")
        # link = full_cast_paid_inclueded(link)
        print(link)
        # break
        # Scrape the data from the website
        data = scrape_all_details(link)
        # Call the insert_data method to insert the data into the table
        db.insert_data(data)
        # Increment the page number
        start_page += 1
        # Wait for 5 seconds before scraping the next page
        time.sleep(3)
        # break
    db.close_db()

# Arts & Entertainment                            
# Music                                           
# Art                                             
# Entertainment & Performing Arts                 
# Computers & Technology                          
# Education & Learning                            
# Education                                       
# Erotica                                         
# Comedy & Humor                                  
# Literature & Fiction                            
# Genre Fiction                                   
# Psychological                                   
# Coming of Age                                   
# Biographies & Memoirs                           
# True Crime                                      
# Adventurers, Explorers & Survival               
# Professionals & Academics                       
# Teen & Young Adult                              
# Romance                                         
# Money & Finance                                 
# Mystery, Thriller & Suspense                    
# Relationships, Parenting & Personal Development 

# Call the insert_data method to insert the data into the table
# db.insert_data(data)
# db.close_db()