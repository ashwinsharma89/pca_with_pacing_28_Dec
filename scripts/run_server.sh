export DATABASE_URL=sqlite:///pca_agent.db
export JWT_SECRET_KEY=test-secret-key-must-be-long-enough-32-chars
export PYTHONPATH=$PYTHONPATH:.
python3 -m src.api.main_v3
