import yaml

SERVICES = [
    "catalog",
    "cart",
    "checkout",
    "pricing",
    "inventory",
    "payment",
    "fulfillment",
    "shipping",
    "notification",
    "search",
    "customer",
    "identity",
    "returns",
    "reviews",
    "recommendation",
]
# "order" is skipped here if we assume the old "api" acts as "order" or we replace "api" completely.
# Let's replace "api" completely with these 16 services and keep the old one as legacy or remove it from docker-compose.
# Actually, the user asked to prioritize a functional Catalog -> Cart -> Checkout -> Order journey.

DOCKER_COMPOSE_PATH = "/Users/advaykankaria/Documents/ai cicd demo/docker-compose.yml"

with open(DOCKER_COMPOSE_PATH, "r") as f:
    compose = yaml.safe_load(f)

base_port = 8010
for i, name in enumerate(SERVICES + ["order"]):
    port = base_port + i
    compose["services"][f"{name}-service"] = {
        "build": {"context": ".", "dockerfile": f"docker/{name}.Dockerfile"},
        "ports": [f"{port}:8000"],
        "environment": [
            "APP_ENV=local",
            "APP_VERSION=1.0.0",
            "DATABASE_URL=postgresql://user:password@postgres:5432/orders",
            "REDIS_URL=redis://redis:6379/0",
            "SIMULATE_FAILURE=${SIMULATE_FAILURE:-false}",
            "FAILURE_SCENARIO=${FAILURE_SCENARIO:-none}",
        ],
        "depends_on": {
            "postgres": {"condition": "service_healthy"},
            "redis": {"condition": "service_healthy"},
        },
    }

with open(DOCKER_COMPOSE_PATH, "w") as f:
    yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

print("docker-compose.yml updated.")
