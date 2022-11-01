import mysql.connector


# Currently there are three table. 
# 'ACTIVE' to store data about active exams and another is 
# 'PREVIOUS' for previous exams
# 'PENDING' for pending exams


class MySQLPool:
  mydb = None
  mycursor = None

  def disconnect(self):
    self.mycursor.close()
    self.mydb.close()
    self.mycursor = None
    self.mydb = None

  def connect(self):
    self.mydb = mysql.connector.connect(
      host="vista.mysql.pythonanywhere-services.com",
      user="vista",
      password="VirtualInstantStudentTest",
      database="vista$default"
    )
    self.mycursor = self.mydb.cursor()

  def execute(self, SQLstring, SQLtuple,SELECT):
    self.connect()
    self.mycursor.execute(SQLstring, SQLtuple)
    res=None
    if SELECT:
        res=self.mycursor.fetchall()
    else:
        self.mydb.commit()
    self.disconnect()
    return res

  def fetch(self):
    return self.mycursor.fetchall()
