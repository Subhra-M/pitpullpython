from fastapi import FastAPI, Body
import requests, os, zipfile, tempfile, shutil

app = FastAPI()

@app.post("/pull-private-repo-unzip")
def pull_private_repo_unzip(
    owner: str = Body(...),
    repo: str = Body(...),
    branch: str = Body("main"),
    destination_dir: str = Body("/workspace/private-repo"),
    github_token: str = Body(...)
):
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    headers = {"Authorization": f"token {github_token}"}

    response = requests.get(url, headers=headers, stream=True)
    if response.status_code != 200:
        return {
            "error": f"GitHub API returned {response.status_code}: {response.text}"
        }

    # Prepare dirs
    os.makedirs(destination_dir, exist_ok=True)
    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        # Write zip
        with open(tmp_zip.name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Extract
        with zipfile.ZipFile(tmp_zip.name, 'r') as zip_ref:
            # GitHub zips have a top-level folder; extract directly
            extract_temp = tempfile.mkdtemp()
            zip_ref.extractall(extract_temp)
            # Move contents of top-level folder to destination_dir
            for item in os.listdir(extract_temp):
                src = os.path.join(extract_temp, item)
                if os.path.isdir(src):
                    for inner in os.listdir(src):
                        shutil.move(os.path.join(src, inner), destination_dir)
                else:
                    shutil.move(src, destination_dir)
            shutil.rmtree(extract_temp)

        return {"extracted_path": destination_dir}

    finally:
        os.unlink(tmp_zip.name)
