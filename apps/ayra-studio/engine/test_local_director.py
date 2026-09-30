import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))

from local_director_provider import LocalDirectorProvider

director = LocalDirectorProvider()

plan = director.create_plan(
    "A young girl discovers a mysterious portal inside an abandoned city."
)

print("AYRA Local Director test: PASS")
print(f"Status: {plan['status']}")
print(f"Mode: {plan['mode']}")
print(f"Concept: {plan['concept']}")
