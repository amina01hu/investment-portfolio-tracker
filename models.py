from db.database import connect_db

# USER CLASS
class User:
    def __init__(self, fname, lname, email, password):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password
        self.user_id = None
        self.portfolio = []

    # method to insert user into the db
    def save(self):
        con = connect_db()
        c = con.cursor()
        try:
            c.execute("""
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (?, ?, ?, ?)
            """, (self.fname, self.lname, self.email, self.password))
            self.user_id = c.lastrowid
            con.commit()
            return True
        except Exception as e:
            print(f"User create error: {e}")
            return False
        finally:
            con.close()
        
    @classmethod
    def find_by_credentials(cls, email, password):
        con = connect_db()
        c = con.cursor()
        c.execute("SELECT * FROM users where email = ? AND password = ?", (email, password))
        data = c.fetchone()
        con.close()
        if data:
            user = cls(data[1], data[2], data[3], data[4])
            user.user_id = data[0]
            return user
        return None
        
    
    @classmethod
    def get_by_id(cls, user_id):
        con = connect_db()
        c = con.cursor()
        c.execute("SELECT * FROM users where id = ?", (user_id, ))
        data = c.fetchone()
        con.close()
        if data:
            user = cls(data[1], data[2], data[3], data[4])
            user.user_id = data[0]
            return user
        return None
    
#PORTFOLIO CLASS
class Portfolio:
    def __init__(self, user_id, name, description):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.portfolio_id = None

    # method to insert the portfolio into the database
    def save(self):
        con = connect_db()
        c = con.cursor()
        try:
            c.execute("""
                INSERT INTO portfolio (user_id, name, description)
                VALUES (?, ?, ?)
            """, (self.user_id, self.name, self.description))
            self.portfolio_id = c.lastrowid
            con.commit()
            con.close()
            return True
        except Exception as e:
            print(f"Portfolio create error: {e}")
            return False
        finally:
            con.close()

    @classmethod
    def get_by_id(cls, user_id):
        con = connect_db()
        c = con.cursor()
        c.execute("SELECT * FROM portfolio where user_id = ?", (user_id,))
        portfolio_data = c.fetchall()
        con.close()
        portfolios = []
        for data in portfolio_data:
            portfolio = cls(data[1], data[2], data[3]) # assuming columns are user_id, name, description
            portfolio.portfolio_id = data[0] # assuming this is the portfolio id
            portfolios.append(portfolio) # add full portfolio to list
        print(portfolios)
        return portfolios
        
       
#ASSET CLASS

class Asset:
    def __init__(self, portfolio_id, symbol, quantity, buy_price, current_price):
        self.portfolio_id = portfolio_id
        self.symbol = symbol
        self.quantity = quantity 
        self.buy_price = buy_price
        self.current_price = current_price
        self.asset_id = None
        
    # method to insert asset into portfolio
    
    def save_to_db(self):
        con = connect_db()
        c = con.cursor()
        try:
            c.execute("""
                INSERT INTO assets (portfolio_id, symbol, quantity, buy_price, current_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.portfolio_id, self.symbol, self.quantity, self.buy_price, self.current_price))
            self.asset_id = c.lastrowid
            con.commit()
            return True
        except Exception as e:
            print(f"Asset create error: {e}")
            return False
        finally:
         con.close()
    
    @classmethod
    def get_by_id(cls, portfolio_id):
        con = connect_db()
        c = con.cursor()
        c.execute("SELECT * FROM assest where portfolio_id = ?", (portfolio_id,))
        asset_data = c.fetchall()
        con.close()
        assets = []
        for data in asset_data:
            asset = cls(data[1], data[2], data[3], data[4], data[5]) # assuming columns are portfolio_id, symbol, quantity, buy_price, current_rpice
            asset.asset_id = data[0] # assuming this is the portfolio id
            assets.append(asset) # add full portfolio to list
        return assets
         
        
        
        
# create a new user
def create_user(first_name, last_name, email, password):
    con = connect_db()
    c = con.cursor()

    # First, check if the user already exists
    existing_user = get_user_by_email(email)

    if existing_user:
        con.close()
        return {"success": False, "message": "User already exists"}
    else:
        # If not, insert new user
        c.execute("""
            INSERT INTO users (first_name, last_name, email, password)
            VALUES (?, ?, ?, ?)
        """, (first_name, last_name, email, password))
        con.commit()
        con.close()
        return {"success": True, "message": "User created succesfully!"}

    
# check if user exists
def get_user_by_email(email):
    con = connect_db()
    c = con.cursor()
    
    # check if user exists
    
    c.execute("SELECT * FROM users where email = ?", (email, ))
    
    existing_user = c.fetchone()
    
    con.close()

    return existing_user

# check if user exists
def get_user_by_id(id):
    con = connect_db()
    c = con.cursor()
    
    # check if user exists
    
    c.execute("SELECT * FROM users where id = ?", (id, ))
    
    existing_user = c.fetchone()
    
    con.close()

    return existing_user
        
        
def update_user_password(email, password):
    # connect to db
    con = connect_db()
    c = con.cursor()
    
    if get_user_by_email(email):
        c.execute("""
                  UPDATE users
                  SET password = ?
                  WHERE email = ?;
                  """, (password, email)
        )
    else:
        print("user does not exist")