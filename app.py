from fastapi import FastAPI, Body
import os, tempfile, zipfile, shutil
import requests

app = FastAPI()
@app.get("/test-function")
def method_abc (self):
    print("I am in testing gitpull. ")

@app.post("/pull-public-repo-unzip")
def pull_public_repo_unzip(
    owner: str = Body(...),
    repo: str = Body(...),
    branch: str = Body("main"),
    destination_dir: str = Body("/workspace/flask")
):
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        return {"error": f"GitHub returned {response.status_code}: {response.text}"}

    os.makedirs(destination_dir, exist_ok=True)
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    
    try:
        with open(tmp_zip.name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        with zipfile.ZipFile(tmp_zip.name, 'r') as zip_ref:
            temp_extract = tempfile.mkdtemp()
            zip_ref.extractall(temp_extract)

            for item in os.listdir(temp_extract):
                item_path = os.path.join(temp_extract, item)
                if os.path.isdir(item_path):
                    for inner_item in os.listdir(item_path):
                        shutil.move(os.path.join(item_path, inner_item), destination_dir)
                else:
                    shutil.move(item_path, destination_dir)

        return {"extracted_path": destination_dir}

    finally:
        os.unlink(tmp_zip.name)
