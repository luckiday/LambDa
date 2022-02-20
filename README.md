For now:
- runs server and client on same device by default; can hardcode server IP in `client.py` to work on separate devices
- no way of sensing when new project comes into server outside of monitoring server directory

## TODO:
- hardcode server IP in `client.py`
- have server sense when new projects come in
- package client folder as apk

## To run:
1. For now, need to add your `.blend` file in some project directory within the `server` directory. For instance:

    ```
    ├── server
    │   ├── proj_name
    │   │   ├── test.blend
    ```

2. Start the server by doing
  ```
  cd src/server
  python3 server.py
  ```

3. Start new client(s) in other terminal(s).
  ```
  cd src/client
  python3 client.py
  ```

Your project's output should end up in
```
├── server
│   ├── proj_name
│   │   ├── output
│   │   │   ├── 0001.jpg
│   │   │   ├── ...and so on
```
