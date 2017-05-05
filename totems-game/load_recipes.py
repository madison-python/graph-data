from os import environ
from py2neo import Graph, Subgraph, Node, Relationship


graph = Graph(password=environ.get('NEO4J_PASSWORD'))

# Fill up items and relationships before creating them in the graph
items = {}
relationships = []

# Make resource nodes
labels = 'fat_tree skinny_tree rock_1 red_berries blue_berries antler'.split()
items.update({label: Node('item', label=label) for label in labels})

recipes = """
rock_1 + rock_1 = rock_2
rock_1 + antler = club
skinny_tree = branch
rock_2 + rock_2 = arrowhead_1
rock_2 + club = arrowhead_2
branch = stick
fat_tree + arrowhead_1 = sheet
sheet + arrowhead_1 = fibers
fibers = string
stick + fibers + arrowhead_1 = axe_1
skinny_tree + axe_1 = skinny_totem
fat_tree + axe_1 = handle
skinny_totem + arrowhead_1 = skinny_and_bare
skinny_totem + axe_1 = fat_totem
fat_totem + arrowhead_2 = bowl
skinny_and_bare + axe_1 = workbench
red_berries + club + bowl = red_ink
blue_berries + club + bowl = blue_ink
workbench + club + arrowhead_1 = knife
handle + knife = notched_handle
workbench + club + rock_1 = blade
blade + rock_1 = axe_blade
notched_handle + axe_blade = axe_2
fat_tree + axe_2 = stump
stump + arrowhead_1 = bare_stump
stick + knife = brush_handle
brush_handle + string + fibers = paint_brush
""".strip().split('\n')


def make_invention_from_recipe(recipe):
    materials_labels, result_label = recipe.replace(' ', '').split('=')

    # Retrieve materials from items.
    # ASSUMES recipes are in order.
    materials = [items[material] for material in materials_labels.split('+')]

    # Create a new item for the result of the invention.
    result = Node('item', label=result_label)
    items[result_label] = result

    for material in materials:
        relationships.append(Relationship(result, 'REQUIRES', material))


for recipe in recipes:
    make_invention_from_recipe(recipe)

data = Subgraph(nodes=items.values(), relationships=relationships)
graph.create(data)
