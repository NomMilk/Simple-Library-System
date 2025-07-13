#simple user class
class Member:
    def __init__(self, username, password, email):
        self.username = username
        self.password = password  # maybe hash the password later? 
        self.email = email
        def can_request_book(self):
            return True
        def can_manage_users(self):
            return False

#simple guest class
class Guest:
    def __init__(self):
        self.username = "Guest"
    def can_request_book(self):
        return False
    def can_manage_users(self):
        return False
    def is_guest(self):
        return True
        #guest cannot access any functions until logging in/creating an account


#class for members
class LibraryMember(Member):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)

#class for staff
class LibraryStaff(Member):
    def __init__(self, username, password, email):
        super().__init__(username, password, email)
    def can_manage_users(self):#staff can manage users
        return True

#for now just barebones classes, gonna have to integrate into the website later