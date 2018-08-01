**************Project Tittle: University Loan Verification Management System**************


Required Packages to install for Linux environment

Package Name:                          How To Install
                                                                           
1. Python 3.6:                       sudo apt-get install python3.6 
                                                                           
2. PostgreSQL database:              sudo apt-get install postgresql 
                                                                           
3. Python3-pip:                      sudo apt-get install python3-pip
                                                                           
4. Django 2.0.4:                     pip3 install django
                                                                           
5. Pyexcel:                          pip3 install pyexcel
                                                                           
6. Python Pillow (PIL):              pip3 install pillow 
                                                                           
7. Matplotlib:                       pip3 install matplotlib



Database Configurations 

Create PostgreSQL database by using the following commands
    
    1.   psql postgresql
    
    2.   create database ulvms;
    
    3.   grant all privileges on database ulvms to  your_user_name;
    
    4.   \q
    
    5.   cd  database
    
    6.   psql  -U  your_user_name   ulvms < ulvms.pgsql
    
Those 6 commands will import ulvms database to your computer,

Now you have to open ulvms/ulvms/settings.py file and configure database by replacing 'USER' and 'PASSWORD'
with your username and password respectively 

       'USER': 'your_user_name',
       
       'PASSWORD': 'your_password',

Save the file and go back to terminal in ulvms directory where there is manage.py file in it
(you can us ls command to check if you are in the right directory)

Execute the following command to run ulvms application on port 8000

       python3 manage.py runserver localhost:8000
       
Now you will be able to access the application to any local web browser through 'http://localhost:8000' address

User the following credentials to log in

Username,                     Password,                    Role

                                                                                  
1.uloanofficer,           staffuserone,               University Loan Officer 
                                                                                  
2.lbloanofficer,          staffusertwo,               Loanboard officer 
                                                                                  
3.2015-04-02571,          studentpassword,            Student 
                                                                                  

To sign by using barcode you need to plug barcode reader on your computer usb port and run 
the program in barcode_reader directory as follows 

    1.  cd  barcode_reader
    2.  sudo python3 barcode_reader.py
       
Now you can scan barcodes to see the output or response displayed on the program which basically tells 
if you have signed successfully or not. use sample barcodes submitted with this document for testing

Note the program barcode_reader should be executed only when the web application is running,
so make sure web application is running before running barcode_reader program
( if it's not running you can start it by using 'python3 manage.py runserver localhost:8000' command )



