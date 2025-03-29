# Tilemap-Editor

## Description

This is a simple tilemap editor built with Python and Pygame. It allows you to create and edit tilemaps for 2D games. You can add, remove, and edit tiles, as well as save and load tilemaps.

![image](./image.png)

## Features
- Add, remove, and edit tiles
- Save and load tilemaps

## Data Encoding in Tilemap

In this tilemap editor, each tile is represented by a single integer (`packed_value`) that encodes multiple pieces of information about the tile. This encoding is done to optimize memory usage and simplify data storage. Here's how the encoding works:

### Structure of `packed_value`

Each `packed_value` is a 32-bit integer, but only the lower 8 bits are used to store the following information:

| Bits  | Field         | Description                              |
|-------|---------------|------------------------------------------|
| 0-2   | `tile_type`   | The type of the tile (values 0-7).       |
| 3-4   | `tile_rotation` | The rotation of the tile (0°, 90°, 180°, 270°). |
| 5-7   | `tile_height` | The height of the tile (values 0-7).     |

### Encoding Process

The encoding process combines these fields into a single integer using bitwise operations:

```python
packed_value = (tile_height << 5) | (tile_rotation << 3) | (tile_type & 0b111)
```
