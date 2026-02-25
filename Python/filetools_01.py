# Tools for writing and reading data text files
# especially for data that should be stored in a subfolder of the program folder
# (or relative to the program folder like ../data


import os, os.path 

filename = "values.dat"
filename_save = "saved_values.dat"
folder_name = "newdata"

def progfolder():
    """returns dir in which program lives"""
    return os.path.dirname(os.path.abspath(__file__))


class Filetools():
    def __init__(self, foldername, filename):
        # Init with folder and file name
        # default filename is the same for reading and saving
        self.foldername = foldername
        self.filename =  filename
        self.filename_read = self.filename
        self.filename_save = self.filename
        self.progfolder = progfolder()
        self.comment = ""
       

    def datafolder(self):
        # Return name of data folder beneath program folder
        # If this folder does not exist, it is created
        f = os.path.join(self.progfolder, self.foldername)
        if not os.path.exists(f):
            print("Creating ", f)
            os.mkdir(f)
        return f
     

    def full_filename(self):
        # return filename including path
        df = self.datafolder()
        fn = os.path.join(df, self.filename)
        return fn

    def full_filename_read(self):
        # return filename for reading, including path
        df = self.datafolder()
        fn = os.path.join(df, self.filename_read)
        return fn
        
    def full_filename_save(self):
        # return filename for saving, including path
        df = self.datafolder()
        fn = os.path.join(df, self.filename_save)
        return fn    


    def save_data(self, text):
        if self.filename_save:
            # Save text to data file
            fn = self.full_filename_save()
            print("Saving to ", fn)
            if self.comment:
                text = self.comment + '\n' + text
            with open(fn, 'w') as f:
                f.write(text)
        else:
            print("Filename not defined, not saving")

    def read_data(self):
        # Return read text from data file
        fn = self.full_filename_read()
        print("Reading from ", fn)
        with open(fn, 'r') as f:
            text = f.read()
            return text


    def ask_filename_save(self):
        # ask filename (without path)
        s = input("Filename for saving: ")
        if s:
            self.filename_save = s
            
        ##print("filename for saving: ",  self.filename_save) 
        
    def ask_filename_read(self):
        # ask filename (without path)
        s = input("Filename for reading: ")
        if s:
            self.filename_read = s
    
    def ask_filename_read_list(self):
        # List files and allow to choose from a list
        files = self.list_files()
        i = input("File number?")
        self.filename_read = files[int(i)]
        print("File name: ", self.filename_read)
         
        
    
      
    def ask_comment(self):
        # comment is added automatically preceded by a '#'
        s = input("Comment: ")
        if s:
            self.comment = "# " + s
      
    def list_files(self):
        files = os.listdir(self.foldername)
        i = 0
        for file in files:
            print(i, "    ", file)
            i += 1
        
        return files              
#-----------------------------------------------------------------------    
        
    print("Filename for data on PC: ", filename_save)
    print()


if __name__ == "__main__":
    folder = progfolder()
    print ("Program folder: ", folder)
    
    
    file_tools = Filetools("../data2", "data.txt")
    file_tools.filename_save = "saved_data.txt" 
    files = file_tools.list_files()
    print()
    
    file_tools.ask_filename_read_list()
    
    
    
    df = file_tools.datafolder()
    print("Data folder: ", df)
    
    fn = file_tools.full_filename()
    print("Full filename: ", fn)
    
    file_tools.ask_filename_save()
    file_tools.ask_comment()
    
    t = "BLAH BLAH blah --"
    file_tools.save_data(t)
    
    file_tools.filename_read = file_tools.filename_save
    tt = file_tools.read_data()
    print(tt)
    
    file_tools.ask_filename_read()
    t = file_tools.read_data()
    print(t)
    
    
    
    
    
    
