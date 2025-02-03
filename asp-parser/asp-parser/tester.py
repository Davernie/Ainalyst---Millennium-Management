from aspParser import analyze_code_from_file

# Redirect output to a file
import sys

output_filename = "output.txt"
sys.stdout = open(output_filename, "w")

# Analyze the test file
analyze_code_from_file("fileForTesting.py")

# Reset stdout
sys.stdout.close()
sys.stdout = sys.__stdout__

print(f"Analysis completed. Results saved in {output_filename}.")
