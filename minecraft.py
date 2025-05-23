from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.mesh import Mesh

# pip install ursina
app = Ursina()
Sky()

# Faces of a cube, each face is a list of 4 corner vertices
cube_faces = {
    'top':    [Vec3(0,1,0), Vec3(1,1,0), Vec3(1,1,1), Vec3(0,1,1)],
    'bottom': [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,0,1), Vec3(0,0,1)],
    'left':   [Vec3(0,0,0), Vec3(0,1,0), Vec3(0,1,1), Vec3(0,0,1)],
    'right':  [Vec3(1,0,0), Vec3(1,1,0), Vec3(1,1,1), Vec3(1,0,1)],
    'front':  [Vec3(0,0,1), Vec3(1,0,1), Vec3(1,1,1), Vec3(0,1,1)],
    'back':   [Vec3(0,0,0), Vec3(1,0,0), Vec3(1,1,0), Vec3(0,1,0)],
}

# Texture coordinates (UVs) for each corner of a face
face_uvs = [Vec2(0,0), Vec2(1,0), Vec2(1,1), Vec2(0,1)]
# Define two triangles (using indices) that make up the quad face
# GPUs render only triangles. Even quads are split into triangles internally
face_triangles = [0, 1, 2, 0, 2, 3]


CHUNK_SIZE = 16
RENDER_DISTANCE = 3
generated_chunks = {} # dictionary to avoid regenerating chunks
interactive_blocks = []


def generate_chunk(chunk_x, chunk_z):
    if (chunk_x, chunk_z) in generated_chunks: # Skil already generated chunks
        return
    
    vertices = []
    uvs = []
    triangles = []

    index_offset = 0

    # Loop over all blocks in the chunk
    for i in range(CHUNK_SIZE):
        for j in range(CHUNK_SIZE):
            x = chunk_x * CHUNK_SIZE + i
            z = chunk_z * CHUNK_SIZE + j
            y = 0 # flat terrain

            for face in cube_faces.values():
                for v in face:
                    vertices.append(v + Vec3(x, y, z)) # position the face in world space
                uvs += face_uvs
                triangles += [i + index_offset for i in face_triangles]
                index_offset += 4
    
    # Create combined mesh
    mesh = Mesh(
        vertices = vertices,
        uvs = uvs,
        triangles = triangles,
        mode = 'triangle'
    )

    # Create a single entity for the whole chunk
    chunk_entity = Entity(
        model=mesh,
        texture='grass.png',
        collider='mesh',
        parent=scene
    )

    generated_chunks[(chunk_x, chunk_z)] = chunk_entity

# Runs every frame, checks which chunk player is in and generates any missing ones nearby
def update():
    player_chunk_x = floor(player.x / CHUNK_SIZE)
    player_chunk_z = floor(player.z / CHUNK_SIZE)

    # Loads all chunks within player's render distance
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            generate_chunk(player_chunk_x + dx, player_chunk_z +dz)

# Preload initial area
initial_chunk_x = 0
initial_chunk_z = 0

for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
    for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
        generate_chunk(initial_chunk_x + dx, initial_chunk_z + dz)


player = FirstPersonController(y = 8)


def input(key):
    # Close game by pressing 'escape' key
    if key == 'escape':
        application.quit()


app.run()