For now:
- runs server and client on same device (PC)
- only renders 1 frame (to render all frames, just uncomment the line in `server.py` that uses `blender_render_info`)
- no way of sensing when new project comes into server

## TODO:
- hardcode server IP in `client.py`
- send outputs from client back to server
  - problem: how to sense client returning output if `server.accept()` is blocking in `while True` (Jessica: honestly unsure if it's blocking)
- broadcast network to see what clients are available
- have server sense when new projects come in?

## To run:
1. For now, need to add your `.blend` file in some project directory within the `server` directory. For instance:

    ```
    ├── server
    │   ├── proj_name
    │   │   ├── test.blend
    ```

2. Start the server by doing
  ```python3 src/server/server.py```

3. Start new client(s) in other terminal(s).
  ```python3 src/client.client.py```

Your project's output should end up in
```
├── client
│   ├── proj_name
│   │   ├── output
│   │   │   ├── 0001.jpg
│   │   │   ├── ...and so on
```
