# main.py 文件内容
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import polars as pl

app = FastAPI()

web_root = Path(__file__).parent / "web/dist"
data_root = Path(__file__).parent

app.mount("/assets", StaticFiles(directory=web_root/"assets"), name="assets")

def read_csv(path: Path):
    try:
        df = pl.read_csv(path)
        return df.to_dicts()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

def read_json(path: Path):
    try:
        df = pl.read_json(path)
        return df.to_dicts()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

@app.get("/")
def get_root():
    response = FileResponse(web_root / "index.html")
    return response

@app.get("/favicon.ico")
def get_icon():
    return FileResponse(web_root / "favicon.ico")

@app.get("/map")
def list_map():
    map_root = data_root / "map"
    file_list = [x.name for x in map_root.iterdir() if x.is_file()]
    print(file_list)
    return JSONResponse(file_list)

@app.get("/map/{path:path}")
def get_map(path: str):
    map_root = data_root / "map"
    file_path = map_root / path
    if file_path.exists():
        response = JSONResponse(content=read_json(file_path))
    else:
        response = HTTPException(status_code=404, detail="Not Found")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8256)