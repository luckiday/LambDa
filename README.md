For now:
- runs server and worker on same device by default
  - can hardcode server IP in `worker.py` to work on separate devices
- only renders first 2 frames of any project to keep testing short
  - can uncomment lines 105-107, comment out 108, uncomment 182, comment 183 to render whole scene

## TODO:
- hardcode server IP in `client.py`

## To run:
1. Start the server by doing
  ```
  cd src/server
  python3 server.py
  ```

2. Start new worker(s) in other terminal(s).
  ```
  cd src/worker
  python3 worker.py
  ```

3. Start requester(s) in other terminal(s)
  ```
  cd src/requester
  python3 requester.py <PATH_TO_BLEND_FILE>
  ```

Your project's output should end up in
```
├── requester
│   ├── random_proj_name
│   │   ├── outputs
│   │   │   ├── 0001.jpg
│   │   │   ├── ...and so on
```
