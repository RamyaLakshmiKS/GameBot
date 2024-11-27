import subprocess

def main():
    subprocess.run(["streamlit", "run", "src/cowculator/app.py"])

if __name__ == "__main__":
    main()