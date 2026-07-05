def read_data():
    try:
        f = open("data.txt", "r")  
        f.close()
        return True
    except Exception as e:
        return f"Some error {e}"
