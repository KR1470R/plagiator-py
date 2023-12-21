# plagiator-py
## Description
Plagiarism detector, which uses the [edubirdie service](https://edubirdie.com/perevirka-na-plagiat) under the hood. It helps you to check approximate uniqueness of the document. Nice tool for school/college/university course/diploma projects.
## Supportable documents formats

 - pdf
 - docx
 - doc
 - txt
## OS compatibility
Linux/MacOS
Windows is under the question due to i didn't tested, but should work respectively. 
## Installation
```bash
git clone git@github.com:KR1470R/plagiator-py.git && cd plagiator-py
python -m venv .venv && source .venv/bin/activate
pip install -r requrements.txt
```
## Usage
The tool will be ready to use straight up after install.
Run the command inside the project directory:
```bash
python -m main
```
It will ask you to specify absolute path to your document:
![prompt image](https://github.com/KR1470R/plagiator-py/master/blob/assets/prompt.png)
After entering the path and clicking enter the tool will show up the progress and after finish the **average uniqueness percentage** of the text from the document:
![finish image](https://github.com/KR1470R/plagiator-py/master/blob/assets/finish.png)
Also, in the `/results` directory there will be saved more detailed results of the every plagiarism detection in json formats, in which you will see where exactly plagiarism detected and links of sources where specific text from your document matched in the WEB:
![results example image](https://github.com/KR1470R/plagiator-py/master/blob/assets/results_example.png)
