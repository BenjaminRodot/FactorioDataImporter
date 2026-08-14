import json

def get_icon(prototype):
    if "icon" in prototype:
        return prototype["icon"]

    if "icons" in prototype and len(prototype["icons"]) > 0:
        return prototype["icons"][0]["icon"]

    return ""

def transform_id_to_name(item_id):
    return item_id.replace("-", " ").title()

def transform_item(item):
    transformed_item = {
        "id": item["name"],
        "name": transform_id_to_name(item["name"]),
        "description": item.get("description", ""),
        "icon": get_icon(item)
    }

    return transformed_item


def transform_recipe_entry(entry):
    transformed_recipe_entry = {
        "resourceId": entry["name"],
        "resourceType": entry["type"],
        "quantity": entry["amount"]
    }

    return transformed_recipe_entry


def transform_recipe(recipe):
    transformed_recipe = {
        "id": recipe["name"],
        "name": transform_id_to_name(recipe["name"]),
        "craftTime": recipe.get("energy_required", 0.5),
        "inputs": [
            transform_recipe_entry(entry)
            for entry in recipe["ingredients"]
        ],
        "outputs": [
            transform_recipe_entry(entry)
            for entry in recipe["results"]
        ]
    }

    return transformed_recipe


def remove_nonusable_recipes(data):
    usable_recipes = []

    for recipe in data["recipe"].values():
        if recipe.get("parameter", False):
            continue

        if recipe.get("hidden", False):
            continue

        if "ingredients" not in recipe:
            continue

        if "results" not in recipe:
            continue

        usable_recipes.append(transform_recipe(recipe))

    return usable_recipes


def find_resource_types_from_list(recipe_list):
    resource_types = set()

    for recipe in recipe_list:
        for ingredient in recipe["inputs"]:
            resource_types.add(ingredient["resourceType"])

        for result in recipe["outputs"]:
            resource_types.add(result["resourceType"])

    return resource_types


def find_resource_ids(recipe_list):
    resource_ids = {
        "item": set(),
        "fluid": set()
    }

    for recipe in recipe_list:
        for resource in recipe["inputs"] + recipe["outputs"]:
            resource_ids[resource["resourceType"]].add(resource["resourceId"])

    return resource_ids

def find_prototype_by_id(data, resource_id):
    for prototype_category in data.values():
        if not isinstance(prototype_category, dict):
            continue

        if resource_id in prototype_category:
            return prototype_category[resource_id]

    return None

def find_item_prototype(data, item_id):
    for prototype_category in data.values():
        if not isinstance(prototype_category, dict):
            continue

        prototype = prototype_category.get(item_id)

        if prototype is None:
            continue

        if "stack_size" not in prototype:
            continue

        return prototype

    return None

def find_item_prototypes(data, item_ids):
    item_prototypes = []

    for item_id in item_ids:
        prototype = find_item_prototype(data, item_id)

        if prototype is None:
            print(f"Item prototype not found: {item_id}")
            continue

        item_prototypes.append(prototype)

    return item_prototypes

def find_fluid_prototypes(data, fluid_ids):
    fluid_prototypes = []

    for fluid_id in fluid_ids:
        prototype = data["fluid"].get(fluid_id)

        if prototype is None:
            print(f"Fluid prototype not found: {fluid_id}")
            continue

        fluid_prototypes.append(prototype)

    return fluid_prototypes

def transform_fluid(fluid):
    transformed_fluid = {
        "id": fluid["name"],
        "name": transform_id_to_name(fluid["name"]),
        "description": "",
        "icon": get_icon(fluid)
    }

    return transformed_fluid

with open("./data/data-raw-dump.json", "r", encoding="utf-8") as file:
    data = json.load(file)

recipe_list = remove_nonusable_recipes(data)
resource_types = find_resource_types_from_list(recipe_list)
resource_ids = find_resource_ids(recipe_list)

item_ids = resource_ids["item"]
fluid_ids = resource_ids["fluid"]

item_prototypes = find_item_prototypes(
    data,
    resource_ids["item"]
)

fluid_prototypes = find_fluid_prototypes(
    data,
    resource_ids["fluid"]
)

item_list = [transform_item(item) for item in item_prototypes]
fluid_list = [transform_fluid(fluid) for fluid in fluid_prototypes]


with open("./data/recipes.json", "w", encoding="utf-8") as file:
    json.dump(recipe_list, file, indent=2)

with open("./data/items.json", "w", encoding="utf-8") as file:
    json.dump(item_list, file, indent=2)

with open("./data/fluids.json", "w", encoding="utf-8") as file:
    json.dump(fluid_list, file, indent=2)