# Starter Environment for SQLAlchemy

```bash
docker compose up -d

# echo = False
pytest test/

# echo = True
pytest --capture=tee-sys -vv --echo tests/test_blog.py::test_counter
```