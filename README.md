## Key as Proxy
Thanks me later! for who does not have permissions to install B.P.M  -_- at your organization laptop so you can bypass .exe installations ✌

### Prerequisities
- ^Python3.10
- pip install poetry (after python installed)
- SOCKS5 configurator pro extension (Chrome, Edge, Firefox)
- Outline Key (extract key to this format: ss://chacha20-ietf-poly1305:AsDfGhJkLaSdF@ip:port)

### Installation
- git clone [repo_addr]
- cd [pj_path]
- cp .env.example .env
- replace your extracted key inside .env at `remote_addr`
- `source $(poetry env info --path)/Scripts/activate` or `$(poetry env info --path)/bin/activate`
- poetry install

### How to Run?
- `source $(poetry env info --path)/Scripts/activate` or `$(poetry env info --path)/bin/activate`
- python app.py