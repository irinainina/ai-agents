import json
import torch
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

data_dir = Path(__file__).parent / "data"
projects_file = data_dir / "projects.json"
embeddings_file = data_dir / "project_embeddings.pt"

with open(projects_file, "r", encoding="utf-8") as f:
    projects = json.load(f)

texts = [
    f"{p['name']} {' '.join(p['industry'])} "
    f"{' '.join(p['services'])} {' '.join(p['keywords'])}"
    for p in projects
]

embeddings = model.encode(
    texts,
    convert_to_tensor=True,
    normalize_embeddings=True
)

torch.save(embeddings, embeddings_file)
print(f"Embeddings saved to {embeddings_file}")
